import pathlib

import pytest

from pytest_fmu_filter.md import ModelDescription, read_modelDescription


def pytest_addoption(parser):
    group = parser.getgroup("fmus")
    group.addoption(
        "--fmus",
        help="FMU paths",
        nargs="+",
    )


def pytest_generate_tests(metafunc):
    """
    Generate tests based on the FMUs in the specified directory.
    """
    # Get commandline option for FMU paths
    fmus = metafunc.config.getoption("fmus")
    if fmus is None:
        # If no FMU paths are provided, skip the test generation
        return

    # Check if the metafunc has a 'fmu_filter' marker
    fmu_filter = metafunc.definition.get_closest_marker("fmu_filter")
    if fmu_filter is None:
        # If no fmu_filter marker is defined, skip the test generation
        return

    # Load and filter FMUs
    filtered_fmus = []
    for fmu_path in fmus:
        try:
            # Read the modelDescription.xml from the FMU
            md = read_modelDescription(fmu_path)

            # apply the filters
            if _apply_filters(md, fmu_filter.kwargs):
                # If the model passes all filters, add it to the filtered list
                filtered_fmus.append(fmu_path)

        except Exception as e:
            # If there's an error reading the FMU, log it and skip this FMU
            metafunc.config.hook.pytest_warning_recorded(
                warning_message=f"Error reading FMU {fmu_path}: {e}",
                when="setup",
            )

    # Parametrize the test function with the filtered FMUs
    if filtered_fmus:
        metafunc.parametrize(
            "fmu",
            filtered_fmus,
            ids=[str(pathlib.Path(m).resolve()) for m in filtered_fmus],
        )
    else:
        # If no FMUs match the filter, skip the test
        pytest.skip("No FMUs match the specified filters")


def _apply_filters(model_description: ModelDescription, filter_kwargs):
    """
    Apply filters to a model description.

    Args:
        model_description: ModelDescription object
        filter_kwargs: Filter criteria from the fmu_filter marker

    Returns:
        bool: True if the model passes all filters, False otherwise
    """
    if model_description is None:
        return False

    # If any filter is failed, return False
    for key, value in filter_kwargs.items():
        if key == "is_me":
            if value and not model_description.is_me():
                return False
            elif value is False and model_description.is_me():
                return False
        elif key == "is_cs":
            if value and not model_description.is_cs():
                return False
            elif value is False and model_description.is_cs():
                return False
        elif key == "is_se":
            if value and not model_description.is_se():
                return False
            elif value is False and model_description.is_se():
                return False
        elif key == "with_inputs":
            if not model_description.with_inputs(value):
                return False
        elif key == "with_outputs":
            if not model_description.with_outputs(value):
                return False
        elif key == "name_matches":
            if not model_description.name_matches(value):
                return False
        elif key == "custom" and callable(value):
            if not value(model_description):
                return False
        elif key == "has_input":
            if value and not model_description.has_input():
                return False
            elif value is False and model_description.has_input():
                return False
        elif key == "has_output":
            if value and not model_description.has_output():
                return False
            elif value is False and model_description.has_output():
                return False
        elif key == "has_parameter":
            if value and not model_description.has_parameter():
                return False
            elif value is False and model_description.has_parameter():
                return False
        elif key == "with_variables":
            if not model_description.with_variables(value):
                return False
        elif key == "with_parameters":
            if not model_description.with_parameters(value):
                return False
        elif key == "fmi_major_version":
            if not model_description.fmi_version.startswith(str(value)):
                return False
        elif key == "fmi_version":
            if model_description.fmi_version != value:
                return False
        else:
            raise ValueError(f"Unknown filter key: {key}")

    # If all filters passed, return True
    return True


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "fmu_filter: Filter FMUs based on specific criteria.",  # avoid warning about unknown markers
    )
