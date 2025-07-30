from __future__ import annotations

from .baseacquisition import BaseAcquisition, EntryReader
from .standardacquisition import StandardAcquisition


class ZSeriesBaseAcquisition(BaseAcquisition):
    """
    A 'z series acquisition' is considered as a series of _StandardAcquisition.
    Registered scan can be split according to translation_z value.

    At the moment there is three version of z-series:

    #. **version 1**: each z is part of the same sequence. bliss .h5 will look like:
        * 1.1    tomo:zserie                                          -> define the beginning of the sequence
        * 2.1    reference images1 (flats)                            -> start of the first z level
        * 3.1    projections 1 -7000 (flats)
        * 4.1    static images (alignment / return projections)
        * 5.1    reference images1 (flats)
        * 6.1    dark images
        * 7.1    reference images1 (flats)                            -> start of the second z level. using `get_z` to know the different levels
        * 8.1    projections 1 -7000 (flats)
        * ...
        in this case an instance of ZSeriesBaseAcquisition will create N NXtomo (one nxtomo per sequence)

    #. **version 2**: each z is part of a new sequence. So each sequence will instantiate ZSeriesBaseAcquisition and each with a single z.
        * 1.1    tomo:zserie                                          -> define the beginning of the sequence
        * 2.1    reference images1 (flats)                            -> start of the first z level
        * 3.1    projections 1 -7000 (flats)
        * 4.1    static images (alignment / return projections)
        * 5.1    reference images1 (flats)
        * 6.1    dark images
        * 7.1    tomo:zserie                                          -> define the beginning of the sequence
        * 8.1    reference images1 (flats)                            -> start of the second z level. using `get_z` to know the different levels
        * 9.1    projections 1 -7000 (flats)
        * ...
        in this case an instance of ZSeriesBaseAcquisition will create one NXtomo (one NXtomo per sequence)


    #. **version 3**: same as version 2 but dark / flat can only be done in a at the beginning or at the end of the series. And we want to copy those.
    To keep compatibility and design this part is done in post-processing.
        in this case an instance of ZSeriesBaseAcquisition will also create one NXtomo (one NXtomo per sequence)

    The goal of this class is mostly to handle the version 1.
    For version 2 and 3 it will be instantiated but `_acquisition` will contain a single acquisition.
    But to manipulate the series in the case of version 2 and especially version 3 the converter will group them inside `_z_series_v2_v3`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._acquisitions: tuple[float, StandardAcquisition] = {}
        """key is z value and value is StandardAcquisition"""
        (
            self._dark_at_start,
            self._dark_at_end,
            self._flat_at_start,
            self._flat_at_end,
        ) = self.get_dark_flat_pos_info()

    def get_dark_flat_pos_info(self) -> tuple:
        #  on latest z-series dark can be saved only at the beginning / end
        # so we need to copy those in post processing
        if self.root_url is None:
            return None, None, None, None
        with EntryReader(self.root_url) as entry:
            scan_flags_grp = self._get_scan_flags(entry_node=entry) or {}
            dark_at_start_dataset = scan_flags_grp.get("dark_images_at_start", None)
            if dark_at_start_dataset is not None:
                dark_at_start_dataset = h5py_read_dataset(dark_at_start_dataset)
            dark_at_end_dataset = scan_flags_grp.get("dark_images_at_end", None)
            if dark_at_end_dataset is not None:
                dark_at_end_dataset = h5py_read_dataset(dark_at_end_dataset)
            flat_at_start_dataset = scan_flags_grp.get(
                "ref_images_at_start", scan_flags_grp.get("flat_images_at_start", None)
            )
            if flat_at_start_dataset is not None:
                flat_at_start_dataset = h5py_read_dataset(flat_at_start_dataset)
            flat_at_end_dataset = scan_flags_grp.get(
                "ref_images_at_end", scan_flags_grp.get("flat_images_at_end", None)
            )
            if flat_at_end_dataset is not None:
                flat_at_end_dataset = h5py_read_dataset(flat_at_end_dataset)

        return (
            dark_at_start_dataset,
            dark_at_end_dataset,
            flat_at_start_dataset,
            flat_at_end_dataset,
        )

    def get_expected_nx_tomo(self):
        return 1

    def get_standard_sub_acquisitions(self) -> tuple:
        """
        Return the tuple of all :class:`.StandardAcquisition` composing
        _acquisitions
        """
        return tuple(self._acquisitions.values())

    def get_z(self, entry):
        if not isinstance(entry, h5py.Group):
            raise TypeError("entry: expected h5py.Group")
        z_array: pint.Quantity | None = self._get_translation_z(entry, n_frame=None)[0]
        if z_array is None:
            raise ValueError(f"No z found for scan {entry.name}")
        z_array = z_array.to_base_units().magnitude
        if isinstance(z_array, numpy.ndarray):
            z_array = set(z_array)
        else:
            z_array = set((z_array,))

        # might need an epsilon here ?
        if len(z_array) > 1:
            raise ValueError(f"More than one value of z found for {entry.name}")
        else:
            return z_array.pop()

    @docstring(BaseAcquisition.register_step)
    def register_step(
        self, url: DataUrl, entry_type, copy_frames: bool = False
    ) -> None:
        """

        :param url:
        """
        with EntryReader(url) as entry:
            z = self.get_z(entry)
        if z not in self._acquisitions:
            new_acquisition = StandardAcquisition(
                root_url=url,
                configuration=self.configuration,
                detector_sel_callback=self._detector_sel_callback,
                start_index=self.start_index + len(self._acquisitions),
                parent=self,
            )
            new_acquisition._dark_at_start = self._dark_at_start
            new_acquisition._flat_at_start = self._flat_at_start
            new_acquisition._dark_at_end = self._dark_at_end
            new_acquisition._flat_at_end = self._flat_at_end
            self._acquisitions[z] = new_acquisition
        self._acquisitions[z].register_step(
            url=url, entry_type=entry_type, copy_frames=copy_frames
        )
