"""
Module for handling FMU modelDescription.xml files across FMI standards.

This module provides functionality to read and parse modelDescription.xml files
from FMUs that are compliant with FMI 2.0 and 3.0 standards.
"""

import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Define namespaces for different FMI versions
FMI_NAMESPACES = {
    "2.0": "http://www.modelica.org/XSD/modelDescription",
    "3.0": "http://www.fmi-standard.org/schemas/3.0",
}


class VariableCausality(str, Enum):
    """Enumeration for variable causality types."""

    PARAMETER = "parameter"
    CALCULATED_PARAMETER = "calculatedParameter"
    INPUT = "input"
    OUTPUT = "output"
    LOCAL = "local"
    INDEPENDENT = "independent"
    STRUCTURAL_PARAMETER = "structuralParameter"


class VariableVariability(str, Enum):
    """Enumeration for variable variability types."""

    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"


class VariableInitial(str, Enum):
    """Enumeration for variable initial types."""

    EXACT = "exact"
    APPROX = "approx"
    CALCULATED = "calculated"


class FmiType(str, Enum):
    """Enumeration for FMI model types."""

    MODEL_EXCHANGE = "me"
    CO_SIMULATION = "cs"
    SCHEDULED_EXECUTION = "se"


@dataclass
class Dimension:
    """Represents a dimension for array variables in FMI 3.0."""

    start: Optional[str] = None
    value_reference: Optional[str] = None


@dataclass
class BaseVariable:
    """Base class for all FMI variables."""

    name: str
    value_reference: int
    description: Optional[str] = None
    causality: Optional[VariableCausality] = None
    variability: Optional[VariableVariability] = None
    type_name: Optional[str] = None


@dataclass
class Fmi2Variable(BaseVariable):
    """Represents a scalar variable in FMI 2.0."""

    initial: Optional[VariableInitial] = None


@dataclass
class Fmi3Variable(BaseVariable):
    """Represents a variable in FMI 3.0."""

    initial: Optional[VariableInitial] = None
    can_handle_multiple_set_per_time_instant: Optional[bool] = None
    intermediate_update: Optional[bool] = None
    previous: Optional[str] = None
    declared_type: Optional[str] = None
    dimensions: List[Dimension] = field(default_factory=list)
    type_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class ModelInterfaceType:
    """Represents a model interface type (ME, CS, SE)."""

    model_identifier: str
    fmi_type: FmiType


@dataclass
class DefaultExperiment:
    """Represents default experiment settings."""

    start_time: Optional[float] = None
    stop_time: Optional[float] = None
    tolerance: Optional[float] = None
    step_size: Optional[float] = None


@dataclass
class BaseModelDescription:
    """Base class for FMI model descriptions."""

    model_name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    interface_types: List[ModelInterfaceType] = field(default_factory=list)
    default_experiment: Optional[DefaultExperiment] = None
    variables: List[Any] = field(default_factory=list)


@dataclass
class Fmi2ModelDescription(BaseModelDescription):
    """FMI 2.0 Model Description."""

    guid: str = ""


@dataclass
class Fmi3ModelDescription(BaseModelDescription):
    """FMI 3.0 Model Description."""

    instantiation_token: str = ""


class ModelDescription:
    """
    Class representing a parsed modelDescription.xml file from an FMU.

    Attributes:
        root (ET.Element): The root XML element of the modelDescription
        fmi_version (str): The FMI standard version ('2.0' or '3.0')
        model: The parsed model description as dataclass (Fmi2ModelDescription or Fmi3ModelDescription)
        namespace (str): The XML namespace for the FMI version
        has_inputs (bool): Whether the model has input variables
        has_outputs (bool): Whether the model has output variables
    """

    def __init__(self, root: ET.Element, fmi_version: str):
        """
        Initialize a ModelDescription from an XML root element.

        Args:
            root: The root XML element of the modelDescription
            fmi_version: The FMI standard version ('2.0' or '3.0')
        """
        self.root = root
        self.fmi_version = fmi_version
        if fmi_version.startswith("1."):
            raise ValueError(
                "FMI 1.0 is not supported. Only FMI 2.0 and 3.0 are supported."
            )

        self.namespace = FMI_NAMESPACES.get(fmi_version, "")

        # Parse model description
        if fmi_version == "2.0":
            self.model = self._parse_fmi2_model()
        elif fmi_version == "3.0":
            self.model = self._parse_fmi3_model()
        else:
            raise ValueError(
                f"Unsupported FMI version: {fmi_version}. Only '2.0' and '3.0' are supported."
            )

    def _parse_fmi2_model(self) -> Fmi2ModelDescription:
        """Parse FMI 2.0 model description."""
        # Basic model attributes
        model_name = self.root.get("modelName", "")
        guid = self.root.get("guid", "")
        description = self.root.get("description", "")
        author = self.root.get("author", "")
        version = self.root.get("version", "")

        # Create model description
        model = Fmi2ModelDescription(
            model_name=model_name,
            guid=guid,
            description=description,
            author=author,
            version=version,
        )

        # Parse interface types
        model.interface_types = self._parse_fmi2_interface_types()

        # Parse default experiment
        model.default_experiment = self._parse_default_experiment()

        # Parse variables
        model.variables = self._parse_fmi2_variables()

        return model

    def _parse_fmi3_model(self) -> Fmi3ModelDescription:
        """Parse FMI 3.0 model description."""
        # Basic model attributes
        model_name = self.root.get("modelName", "")
        instantiation_token = self.root.get("instantiationToken", "")
        description = self.root.get("description", "")
        author = self.root.get("author", "")
        version = self.root.get("version", "")

        # Create model description
        model = Fmi3ModelDescription(
            model_name=model_name,
            instantiation_token=instantiation_token,
            description=description,
            author=author,
            version=version,
        )

        # Parse interface types
        model.interface_types = self._parse_fmi3_interface_types()

        # Parse default experiment
        model.default_experiment = self._parse_default_experiment()

        # Parse variables
        model.variables = self._parse_fmi3_variables()

        return model

    def _parse_fmi2_interface_types(self) -> List[ModelInterfaceType]:
        """Parse model interface types for FMI 2.0."""
        interface_types = []

        # Check for ModelExchange
        me_element = self.root.find("./ModelExchange")
        if me_element is not None:
            me_model_id = me_element.get("modelIdentifier", "")
            if me_model_id:
                interface_types.append(
                    ModelInterfaceType(
                        model_identifier=me_model_id, fmi_type=FmiType.MODEL_EXCHANGE
                    )
                )

        # Check for CoSimulation
        cs_element = self.root.find("./CoSimulation")
        if cs_element is not None:
            cs_model_id = cs_element.get("modelIdentifier", "")
            if cs_model_id:
                interface_types.append(
                    ModelInterfaceType(
                        model_identifier=cs_model_id, fmi_type=FmiType.CO_SIMULATION
                    )
                )

        return interface_types

    def _parse_fmi3_interface_types(self) -> List[ModelInterfaceType]:
        """Parse model interface types for FMI 3.0."""
        interface_types = []

        # Check for ModelExchange
        me_element = self.root.find("./ModelExchange")
        if me_element is not None:
            me_model_id = me_element.get("modelIdentifier", "")
            if me_model_id:
                interface_types.append(
                    ModelInterfaceType(
                        model_identifier=me_model_id, fmi_type=FmiType.MODEL_EXCHANGE
                    )
                )

        # Check for CoSimulation
        cs_element = self.root.find("./CoSimulation")
        if cs_element is not None:
            cs_model_id = cs_element.get("modelIdentifier", "")
            if cs_model_id:
                interface_types.append(
                    ModelInterfaceType(
                        model_identifier=cs_model_id, fmi_type=FmiType.CO_SIMULATION
                    )
                )

        # Check for ScheduledExecution (new in FMI 3.0)
        se_element = self.root.find("./ScheduledExecution")
        if se_element is not None:
            se_model_id = se_element.get("modelIdentifier", "")
            if se_model_id:
                interface_types.append(
                    ModelInterfaceType(
                        model_identifier=se_model_id,
                        fmi_type=FmiType.SCHEDULED_EXECUTION,
                    )
                )

        return interface_types

    def _parse_default_experiment(self) -> Optional[DefaultExperiment]:
        """Parse default experiment settings."""
        # Look for DefaultExperiment element
        default_exp = self.root.find("./DefaultExperiment")
        if default_exp is None:
            return None

        # Extract experiment settings and convert to float
        start_time_str = default_exp.get("startTime")
        stop_time_str = default_exp.get("stopTime")
        tolerance_str = default_exp.get("tolerance")
        step_size_str = default_exp.get("stepSize")

        # Convert strings to float if they exist
        start_time = float(start_time_str) if start_time_str is not None else None
        stop_time = float(stop_time_str) if stop_time_str is not None else None
        tolerance = float(tolerance_str) if tolerance_str is not None else None
        step_size = float(step_size_str) if step_size_str is not None else None

        return DefaultExperiment(
            start_time=start_time,
            stop_time=stop_time,
            tolerance=tolerance,
            step_size=step_size,
        )

    def _parse_fmi2_variables(self) -> List[Fmi2Variable]:
        """Parse variables for FMI 2.0."""
        variables = []

        # FMI 2.0: Variables are in ModelVariables/ScalarVariable
        for var in self.root.findall("./ModelVariables/ScalarVariable"):
            name = var.get("name")
            if name is None:
                raise ValueError("Variable name is required but not found.")
            value_reference = var.get("valueReference")
            if value_reference is None:
                raise ValueError("Variable valueReference is required but not found.")
            value_reference = int(value_reference)
            description = var.get("description")

            # Parse causality
            causality_str = var.get("causality", "local")
            try:
                causality = VariableCausality(causality_str)
            except ValueError:
                causality = None

            # Parse variability
            variability_str = var.get("variability", "continuous")
            try:
                variability = VariableVariability(variability_str)
            except ValueError:
                variability = None

            # Parse initial
            initial_str = var.get("initial")
            try:
                initial = VariableInitial(initial_str) if initial_str else None
            except ValueError:
                initial = None

            # Determine type from child element
            type_name = None
            for type_elem in ["Real", "Integer", "Boolean", "String", "Enumeration"]:
                if var.find(f"./{type_elem}") is not None:
                    type_name = type_elem.lower()
                    break

            # Create variable
            variable = Fmi2Variable(
                name=name,
                value_reference=value_reference,
                description=description,
                causality=causality,
                variability=variability,
                type_name=type_name,
                initial=initial,
            )

            variables.append(variable)

        return variables

    def _parse_fmi3_variables(self) -> List[Fmi3Variable]:
        """Parse variables for FMI 3.0."""
        variables = []

        # FMI 3.0 variable types
        fmi3_types = [
            "Float32",
            "Float64",
            "Int8",
            "UInt8",
            "Int16",
            "UInt16",
            "Int32",
            "UInt32",
            "Int64",
            "UInt64",
            "Boolean",
            "String",
            "Binary",
            "Enumeration",
        ]

        # Find ModelVariables element
        model_variables = self.root.find("./ModelVariables")
        if model_variables is None:
            return variables

        # Process each variable type
        for type_elem in fmi3_types:
            for var in model_variables.findall(f"./{type_elem}"):
                name = var.get("name")
                if name is None:
                    raise ValueError(
                        f"Variable name is required but not found in {type_elem} variable"
                    )

                value_reference = var.get("valueReference")
                if value_reference is None:
                    raise ValueError(
                        f"ValueReference is required but not found for variable {name}"
                    )
                value_reference = int(value_reference)

                description = var.get("description")

                # Parse causality
                causality_str = var.get("causality", "local")
                try:
                    causality = VariableCausality(causality_str)
                except ValueError:
                    causality = None

                # Parse variability
                variability_str = var.get("variability", "continuous")
                try:
                    variability = VariableVariability(variability_str)
                except ValueError:
                    variability = None

                # Parse initial
                initial_str = var.get("initial")
                try:
                    initial = VariableInitial(initial_str) if initial_str else None
                except ValueError:
                    initial = None

                # Parse FMI 3.0 specific attributes
                can_handle_multiple_set = var.get("canHandleMultipleSetPerTimeInstant")
                if can_handle_multiple_set is not None:
                    can_handle_multiple_set = can_handle_multiple_set.lower() == "true"

                intermediate_update = var.get("intermediateUpdate")
                if intermediate_update is not None:
                    intermediate_update = intermediate_update.lower() == "true"

                previous = var.get("previous")
                declared_type = var.get("declaredType")

                # Extract type-specific attributes (like start values, min, max, etc.)
                type_attributes = {}
                for attr_name, attr_value in var.attrib.items():
                    # Skip attributes already processed
                    if attr_name not in [
                        "name",
                        "valueReference",
                        "description",
                        "causality",
                        "variability",
                        "initial",
                        "canHandleMultipleSetPerTimeInstant",
                        "intermediateUpdate",
                        "previous",
                        "declaredType",
                    ]:
                        type_attributes[attr_name] = attr_value

                # Process start value for String and Binary which have it as a child element
                start_elem = var.find("./Start")
                if start_elem is not None and "start" not in type_attributes:
                    type_attributes["start"] = start_elem.get("value", "")

                # Process dimensions for array variables
                dimensions = []
                dim_elements = var.findall("./Dimension")
                for dim in dim_elements:
                    start = dim.get("start")
                    value_ref = dim.get("valueReference")
                    dimensions.append(Dimension(start=start, value_reference=value_ref))

                # Create the variable object
                variable = Fmi3Variable(
                    name=name,
                    value_reference=value_reference,
                    description=description,
                    causality=causality,
                    variability=variability,
                    type_name=type_elem.lower(),
                    initial=initial,
                    can_handle_multiple_set_per_time_instant=can_handle_multiple_set,
                    intermediate_update=intermediate_update,
                    previous=previous,
                    declared_type=declared_type,
                    dimensions=dimensions,
                    type_attributes=type_attributes,
                )

                variables.append(variable)

        return variables

    def is_me(self) -> bool:
        """Check if the FMU supports Model Exchange."""
        return any(
            it.fmi_type == FmiType.MODEL_EXCHANGE for it in self.model.interface_types
        )

    def is_cs(self) -> bool:
        """Check if the FMU supports Co-Simulation."""
        return any(
            it.fmi_type == FmiType.CO_SIMULATION for it in self.model.interface_types
        )

    def is_se(self) -> bool:
        """Check if the FMU supports Scheduled Execution (FMI 3.0 only)."""
        return any(
            it.fmi_type == FmiType.SCHEDULED_EXECUTION
            for it in self.model.interface_types
        )

    def name_matches(self, pattern: str) -> bool:
        """Check if the model name matches the given regex pattern."""
        return re.search(pattern, self.model.model_name) is not None

    def with_variables(self, variables: list[str] | str) -> bool:
        """
        Check if the model has variables with names matching the provided list.

        Args:
            variables: List of variable names to check

        Returns:
            True if any variable name matches, False otherwise
        """
        if isinstance(variables, str):
            variables = [variables]
        # Check if any of the variable names match the provided list
        return any(
            var.name in variables
            for var in self.model.variables
            if hasattr(var, "name")
        )

    def has_input(self) -> bool:
        """Check if the model has input variables."""
        return any(
            getattr(var, "causality", None) == VariableCausality.INPUT
            for var in self.model.variables
        )

    def has_output(self) -> bool:
        """Check if the model has output variables."""
        return any(
            getattr(var, "causality", None) == VariableCausality.OUTPUT
            for var in self.model.variables
        )

    def has_parameter(self) -> bool:
        """Check if the model has parameter variables."""
        return any(
            getattr(var, "causality", None) == VariableCausality.PARAMETER
            for var in self.model.variables
        )

    def with_inputs(self, inputs: list[str] | str) -> bool:
        """Check if the model has input variables."""
        if isinstance(inputs, str):
            inputs = [inputs]
        if not self.has_input:
            return False
        # Check if any of the input variable names match the provided list
        return any(
            var.name in inputs for var in self.model.variables if hasattr(var, "name")
        )

    def with_outputs(self, outputs: list[str] | str) -> bool:
        """Check if the model has output variables."""
        if isinstance(outputs, str):
            outputs = [outputs]
        if not self.has_output:
            return False
        # Check if any of the output variable names match the provided list
        return any(
            var.name in outputs for var in self.model.variables if hasattr(var, "name")
        )

    def with_parameters(self, parameters: list[str] | str) -> bool:
        """Check if the model has parameter variables."""
        if isinstance(parameters, str):
            parameters = [parameters]
        if not self.has_parameter:
            return False
        # Check if any of the parameter variable names match the provided list
        return any(
            var.name in parameters
            for var in self.model.variables
            if hasattr(var, "name")
        )

    def has_array_variables(self) -> bool:
        """Check if the FMU has any array variables (dimensions)."""
        if self.fmi_version == "3.0":
            # For FMI 3.0, check dimensions attribute of Fmi3Variable
            return any(
                isinstance(var, Fmi3Variable) and len(var.dimensions) > 0
                for var in self.model.variables
            )
        return False


def read_modelDescription(fmu_path: Union[str, Path]) -> ModelDescription:
    """
    Read and parse the modelDescription.xml file from an FMU.

    Args:
        fmu_path: Path to the FMU file

    Returns:
        ModelDescription object containing the parsed modelDescription data

    Raises:
        FileNotFoundError: If the FMU file does not exist
        ValueError: If the file is not a valid FMU or does not contain a modelDescription.xml
        Exception: For other errors during parsing
    """
    fmu_path = Path(fmu_path)

    if not fmu_path.exists():
        raise FileNotFoundError(f"FMU file not found: {fmu_path}")

    # If the path is a directory, look for modelDescription.xml directly
    if fmu_path.is_dir():
        md_path = fmu_path / "modelDescription.xml"
        if not md_path.exists():
            raise ValueError(f"No modelDescription.xml found in directory: {fmu_path}")

        try:
            tree = ET.parse(md_path)
            root = tree.getroot()
        except Exception as e:
            raise Exception(f"Error parsing modelDescription.xml: {e}")

    # Otherwise, assume it's a zip file (standard FMU)
    else:
        try:
            with zipfile.ZipFile(fmu_path, "r") as zip_ref:
                # Check if modelDescription.xml exists in the archive
                if "modelDescription.xml" not in zip_ref.namelist():
                    raise ValueError(
                        f"No modelDescription.xml found in FMU: {fmu_path}"
                    )

                # Read and parse modelDescription.xml
                with zip_ref.open("modelDescription.xml") as md_file:
                    try:
                        tree = ET.parse(md_file)
                        root = tree.getroot()
                    except Exception as e:
                        raise Exception(f"Error parsing modelDescription.xml: {e}")
        except zipfile.BadZipFile:
            raise ValueError(f"Not a valid zip file (FMU): {fmu_path}")

    # Determine FMI version
    fmi_version = root.get("fmiVersion", "")

    # Map the version string to our simplified version scheme
    if fmi_version.startswith("2."):
        fmi_version = "2.0"
    elif fmi_version.startswith("3."):
        fmi_version = "3.0"
    else:
        raise ValueError(
            f"Unsupported or unrecognized FMI version: {fmi_version}. Only FMI 2.0 and 3.0 are supported."
        )

    # Create and return ModelDescription object
    return ModelDescription(root, fmi_version)
