import pathlib
import pytest

from pytest_fmu_filter.md import read_modelDescription
from tests.utils import download_reference_fmu


@pytest.mark.parametrize(
    "reference_fmu, fmi_version",
    [("2.0/Feedthrough.fmu", "2.0"), ("3.0/Feedthrough.fmu", "3.0")],
)
def test_fmi_version(reference_fmu, fmi_version, tmpdir):
    filename = download_reference_fmu(reference_fmu, pathlib.Path(tmpdir))
    # load the model description from the FMU
    md = read_modelDescription(filename)

    assert md.fmi_version == fmi_version


@pytest.mark.parametrize(
    "reference_fmu", ["2.0/Feedthrough.fmu", "3.0/Feedthrough.fmu"]
)
def test_has_input(reference_fmu, tmpdir):
    filename = download_reference_fmu(reference_fmu, pathlib.Path(tmpdir))
    # load the model description from the FMU
    md = read_modelDescription(filename)

    assert md.has_input()

    # x = md.get_default_experiment()

    # assert x is not None
    # assert x.start_time == pytest.approx(0.0, abs=1e-6)
    # assert x.stop_time == pytest.approx(3.0, abs=1e-6)
