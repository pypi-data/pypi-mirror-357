# pytest-fmu-filter

[![PyPI version](https://img.shields.io/pypi/v/pytest-fmu-filter.svg)](https://pypi.org/project/pytest-fmu-filter)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-fmu-filter.svg)](https://pypi.org/project/pytest-fmu-filter)
[![See Build Status on GitHub Actions](https://github.com/ticoder00/pytest-fmu-filter/actions/workflows/main.yml/badge.svg)](https://github.com/time-integral/pytest-fmu-filter/actions/workflows/ci.yml)

A pytest plugin to filter and parameterize tests with FMU (Functional Mock-up Unit) files.

## Overview

`pytest-fmu-filter` is a pytest plugin that allows you to easily filter and run tests against specific FMU files based on various criteria. This is particularly useful for testing simulation models that follow the Functional Mock-up Interface (FMI) standard.

The plugin allows you to:
- Specify FMU files via command line arguments
- Filter FMUs based on specific criteria such as:
  - Model Exchange (ME) or Co-Simulation (CS) interface type
  - Presence of inputs or outputs
  - Name patterns
  - Custom filter functions

## When/Why to Use

`pytest-fmu-filter` is ideal for cases where you have multiple FMU files and want to selectively run tests against them based on their properties. This can help you:
- Focus on specific models that are relevant to your current testing needs
- Avoid running tests on FMUs that do not meet certain criteria, saving time and resources

## Requirements

- Python 3.10 or higher
- pytest 7.0.0 or higher

## Installation

Install "pytest-fmu-filter" with `uv` (to dev group):

```bash
uv add pytest-fmu-filter --dev
```

## Usage

### Basic Usage

1. Specify FMU files when running pytest:

```bash
pytest --fmus path/to/model1.fmu path/to/model2.fmu
```

2. Mark test functions with the `fmu_filter` marker to apply filters:

```python
import pytest

@pytest.mark.fmu_filter(is_me=True)  # Only run with Model Exchange FMUs
def test_model_exchange_fmu(fmu):
    # Your test code here
    assert fmu is not None
```

### Available Filter Options

The following filter options are supported in the `fmu_filter` marker:

#### Interface Type Filters
- `is_me`: Filter FMUs that support Model Exchange
- `is_cs`: Filter FMUs that support Co-Simulation
- `is_se`: Filter FMUs that support Scheduled Execution (FMI 3.0 only)

#### Variable-Related Filters
- `has_input`: Filter FMUs that have any input variables
- `has_output`: Filter FMUs that have any output variables
- `has_parameter`: Filter FMUs that have any parameter variables
- `with_variables`: Filter FMUs that have specific variable names
- `with_inputs`: Filter FMUs that have specific input variable names
- `with_outputs`: Filter FMUs that have specific output variable names
- `with_parameters`: Filter FMUs that have specific parameter variable names
- `has_array_variables`: Filter FMUs that have array variables (FMI 3.0 only)

#### Model Information Filters
- `name_matches`: Filter FMUs by regex pattern matching the model name

#### Custom Filters
- `custom`: Provide a custom filter function that takes a ModelDescription object

#### Examples:

```python
# Filter by interface type
@pytest.mark.fmu_filter(is_cs=True)
def test_cosimulation_fmu(fmu):
    # Test will only run with FMUs that support Co-Simulation
    pass

# Filter by variable existence
@pytest.mark.fmu_filter(has_input=True, has_output=True)
def test_fmu_with_io(fmu):
    # Test will only run with FMUs that have both inputs and outputs
    pass

# Filter by specific variable names
@pytest.mark.fmu_filter(with_inputs=["position", "velocity"])
def test_position_control(fmu):
    # Test will only run with FMUs that have input variables named "position" and "velocity"
    pass

# Filter by name pattern
@pytest.mark.fmu_filter(name_matches="Robot.*Controller")
def test_robot_controller(fmu):
    # Test will only run with FMUs that have names matching the regex "Robot.*Controller"
    pass

# Combine multiple filters
@pytest.mark.fmu_filter(is_me=True, has_parameter=True, name_matches=".*Model.*")
def test_parameterized_model(fmu):
    # Test will only run with Model Exchange FMUs that have parameters and "Model" in their name
    pass
```

## License

Distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license, "pytest-fmu-filter" is free and open source software.

## Issues

If you encounter any problems, please [file an issue](https://github.com/ticoder00/pytest-fmu-filter/issues) along with a detailed description.
