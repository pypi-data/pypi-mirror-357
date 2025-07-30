from typing import Sequence

from ewokscore import Task
from ImageD11.unitcell import unitcell as UnitCell
from pydantic import Field

from ..filtering import filter_with_indexer
from ..models import InputsWithOverwrite
from ..nexus.parameters import (
    find_lattice_parameters,
    find_reciprocal_distance_tolerance,
    find_wavelength,
)
from ..nexus.peaks import read_peaks_attributes, save_nexus_process
from ..nexus.utils import (
    check_throw_write_data_group_url,
    get_data_url_paths,
    get_entry_name,
)


class Inputs(InputsWithOverwrite):
    intensity_filtered_data_url: str = Field(
        description="Path to the NXprocess group containing the intensity filtered peaks"
    )
    rings: Sequence[int] = Field(
        description="Ring indices",
        examples=[(0, 1, 2)],
    )
    process_group_name: str = Field(
        default="indexer_filtered_peaks",
        description="NXprocess group name where to save the filtered peaks",
    )


class FilterByIndexer(
    Task,
    input_model=Inputs,
    output_names=["indexer_filtered_data_url"],
):
    """
    Filter the 3D merged peaks using Indexer, to be used only to grid indexer for producing grains.

    Outputs:

    - `indexer_filtered_data_url` (str): Data path to 'NxProcess group data' Grains that stores generated UBI

    """

    def run(self):
        inputs = Inputs(**self.get_input_values())
        nexus_file_path, intensity_filtered_data_group_path = get_data_url_paths(
            inputs.intensity_filtered_data_url
        )

        entry_name = get_entry_name(intensity_filtered_data_group_path)
        output_process_path = f"{entry_name}/{inputs.process_group_name}"
        check_throw_write_data_group_url(
            overwrite=inputs.overwrite,
            filename=nexus_file_path,
            data_group_path=output_process_path,
        )

        intensity_filtered_peaks = read_peaks_attributes(
            filename=nexus_file_path, process_group=intensity_filtered_data_group_path
        )
        lattice_parameters, space_group = find_lattice_parameters(
            inputs.intensity_filtered_data_url
        )
        unit_cell = UnitCell(
            lattice_parameters=lattice_parameters,
            symmetry=str(space_group),
        )
        phase_ds_tolerance = find_reciprocal_distance_tolerance(
            data_url_as_str=inputs.intensity_filtered_data_url
        )

        index_filtered_peaks = filter_with_indexer(
            peak_3d_dict=intensity_filtered_peaks,
            unit_cell=unit_cell,
            wavelength=find_wavelength(inputs.intensity_filtered_data_url),
            phase_ds_tolerance=phase_ds_tolerance,
            rings=inputs.rings,
        )

        nxprocess_url = save_nexus_process(
            filename=nexus_file_path,
            entry_name=entry_name,
            process_name=inputs.process_group_name,
            peaks_data=index_filtered_peaks,
            config_settings={
                "dstol": phase_ds_tolerance,
                "rings": inputs.rings,
                "data_from": inputs.intensity_filtered_data_url,
            },
            pks_axes=("ds", "eta"),
            overwrite=inputs.overwrite,
        )
        self.outputs.indexer_filtered_data_url = nxprocess_url
