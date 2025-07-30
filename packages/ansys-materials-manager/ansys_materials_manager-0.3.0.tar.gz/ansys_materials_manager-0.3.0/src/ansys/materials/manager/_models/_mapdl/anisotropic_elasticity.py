# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from enum import Enum
from typing import Any, List, Optional, Tuple, Union

import numpy as np

from ansys.materials.manager._models._common._base import _BaseModel, _MapdlCore
from ansys.materials.manager._models._common._exceptions import ModelValidationException
from ansys.materials.manager._models._common._packages import SupportedPackage
from ansys.materials.manager.util.common import (
    FLOAT_VALUE_REGEX,
    MATRIX_LABEL_REGEX,
    _chunk_lower_triangular_matrix,
    fill_upper_triangular_matrix,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from ansys.materials.manager.material import Material  # noqa: F401


class ElasticityMode(Enum):
    """Determines which kind of coefficients are used in the model."""

    # Indicates that the model coefficients have units of stiffness, for example GPa
    STIFFNESS = 1

    # Indicates that the model coefficients have units of compliance (inverse stiffness), for
    # example GPa^-1
    COMPLIANCE = 2


class AnisotropicElasticity(_BaseModel):
    r"""
    Provides the anisotropic elasticity model.

    The anisotropic elasticity model defines different elastic coefficients
    for each coordinate axis. This model can be used with plane and solid elements.
    The elastic coefficient matrix (D) is specified as one or up to six NumPy arrays,
    allowing temperature dependence to be modeled.

    The elastic coefficient matrix is defined as a 2 x n_dimensions array:

    .. math::
          \begin{matrix}
            D_{11}\\
            D_{21} & D_{22}\\
            D_{31} & D_{32} & D_{33}\\
            D_{41} & D_{42} & D_{43} & D_44}
          \end{matrix}

    This can either be specified in "stiffness" form, with units of force/area, or in "compliance"
    form with the inverse unit.

    Notes
    -----
    This model wraps the APDL "ELAS" and "ANEL" models in both their forms. If one temperature is
    provided, the "ELAS" model is used, with either the "AELS" or "AELF" TBOPT. Otherwise,
    the "ANEL" model is used.
    """

    _n_dimensions: int
    _coefficient_type: ElasticityMode
    _coefficients: np.ndarray
    _temperature: np.ndarray

    model_codes = ("ANEL", "ELAS")
    _name = "Anisotropic Elasticity"
    applicable_packages = SupportedPackage.MAPDL

    def __init__(
        self,
        n_dimensions: int,
        coefficient_type: ElasticityMode,
        coefficients: Optional[np.ndarray] = None,
        temperature: Union[None, float, np.ndarray] = None,
    ) -> None:
        """
        Create an anisotropic elasticity model.

        Parameters
        ----------
        n_dimensions: int
            Number of dimensions for the model. The value must be either ``2`` or ``3``.
        coefficient_type: ElasticityMode
            Type of elasticity mode that the model uses, which is either stiffness or
            compliance coefficients.
        coefficients: np.ndarray
            Model coefficients, either one 2*n_dims x 2*n_dims array of the model coefficients or,
            if the model is temperature dependent, up to 6 x 2*n_dims x 2*n_dims array of the model
            coefficients at temperature.
        temperature: Union[float, np.ndarray]
            Either a single temperature at which to apply the model or an array of up to
            six temperatures if the model is temperature dependent. If multiple temperatures are
            defined, ensure that they cover the range of anticipated temperatures at which the model
            is applied.
        """
        if n_dimensions not in [2, 3]:
            raise ValueError("n_dimensions must be an integer value of 2 or 3.")
        self._n_dimensions = n_dimensions
        self._coefficient_type = coefficient_type
        self._temperature = np.array([], dtype=float)
        self._coefficients = np.array([], dtype=float)
        if temperature is not None:
            if isinstance(temperature, (float, int)):
                self._temperature = np.array([temperature], dtype=float)
            else:
                self._temperature = temperature
        if coefficients is not None:
            self._coefficients = coefficients

    def __repr__(self) -> str:
        """Apparently this requires a docstring?."""
        return (
            f"<AnisotropicElasticity "
            f"n_dimensions={self._n_dimensions}, "
            f"temperature_count={len(self._temperature)}, "
            f"mode={self._coefficient_type.name}>"
        )

    @property
    def name(self) -> str:
        """Name of the model."""
        return self._name

    @property
    def coefficients(self) -> np.ndarray:
        """Current coefficient array for the model."""
        return self._coefficients

    @coefficients.setter
    def coefficients(self, value: np.ndarray):
        self._coefficients = value

    @property
    def temperature(self) -> np.ndarray:
        """Temperature defined for the model."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: Union[float, np.ndarray]):
        if isinstance(value, (float, int)):
            self._temperature = np.array([value], dtype=float)
        else:
            self._temperature = value

    @classmethod
    def deserialize_model(cls, model_code: str, model_data: List[str]) -> "AnisotropicElasticity":
        """
        Convert output from the MAPDL command into an object representing the model.

        The input should be a section of output referring to one model from one material.

        Parameters
        ----------
        model_code: str
            String model code, either "ELAS" or "ANEL".
        model_data: List[str]
            Lines from MAPDL output corresponding to this model for one material.

        Returns
        -------
        AnisotropicElasticity
            Wrapper for the underlying MAPDL material model.

        Notes
        -----
        Depending on the type of the underlying model, the parameters of the returned
        `AnisotropicElasticity` model vary, but this class is returned for either
        "ELAS" or "ANEL" material models.
        """
        assert model_code in cls.model_codes, f"Invalid model code ({model_code}) provided."
        header_row_index = 0
        for index, line in enumerate(model_data):
            if line.strip().startswith("Temps"):
                header_row_index = index
                break
        if model_code == "ANEL":
            n_dim, temps, coeffs = cls.deserialize_anel_data(
                model_data[header_row_index : header_row_index + 22]
            )
            mode = ElasticityMode.STIFFNESS
            for line in model_data[header_row_index + 23 :]:
                if line.strip().startswith("Flexibility"):
                    mode = ElasticityMode.COMPLIANCE
                    break
            return cls(n_dim, mode, coeffs, temps)

        else:
            n_dim, temp, coeffs = cls.deserialize_elas_data(
                model_data[header_row_index : header_row_index + 22]
            )
            if "STIFFNESS" in model_data[header_row_index - 2]:
                mode = ElasticityMode.STIFFNESS
            else:
                mode = ElasticityMode.COMPLIANCE
            return cls(n_dim, mode, coeffs, temp)

    @staticmethod
    def deserialize_anel_data(
        model_data: List[str],
    ) -> Tuple[int, np.ndarray, np.ndarray]:
        """
        Deserialize the first section of data returned by calling `TBLIST` with an "ANEL" model.

        The first row contains the temperatures at which the model is applied, and subsequent
        rows contain each coefficient value at each specified temperature.

        Parameters
        ----------
        model_data: List[str]
            Lines from MAPDL output corresponding to the model coefficients and measured
            temperatures.
        """
        temp_values = [float(match[0]) for match in FLOAT_VALUE_REGEX.findall(model_data[0])]
        matrix_data = AnisotropicElasticity.read_matrix(model_data[1:])
        coeffs = []
        for temp_index, temp_value in enumerate(temp_values):
            data_at_temp = [row[temp_index + 1] for row in matrix_data]
            if np.allclose(data_at_temp[10:], 0):
                data_at_temp = data_at_temp[0:10]
            coeffs.append(fill_upper_triangular_matrix(data_at_temp))
        if all([matrix.size == 16 for matrix in coeffs]):
            ndim = 2
        else:
            ndim = 3
        coeff_np = np.empty((len(temp_values), 2 * ndim, 2 * ndim))
        for index, matrix in enumerate(coeffs):
            coeff_np[index, 0 : 2 * ndim, 0 : 2 * ndim] = matrix
        return ndim, np.asarray(temp_values, dtype=float), coeff_np

    @staticmethod
    def deserialize_elas_data(model_data: List[str]) -> Tuple[int, float, np.ndarray]:
        """
        Deserialize the first section of data returned by calling `TBLIST` with an "ELAS" model.

        The first row contains the temperature at which the model is applied, and subsequent
        rows contain each coefficient value.

        Parameters
        ----------
        model_data: List[str]
            Lines from MAPDL output corresponding to the model coefficients and measured
            temperature.
        """
        temp_values = float(FLOAT_VALUE_REGEX.findall(model_data[0])[0][0])
        matrix_data = AnisotropicElasticity.read_matrix(model_data[1:])
        data_at_temp = [row[1] for row in matrix_data]
        if np.allclose(data_at_temp[10:], 0):
            data_at_temp = data_at_temp[0:10]
            ndim = 2
        else:
            ndim = 3
        coeffs = fill_upper_triangular_matrix(data_at_temp)
        return ndim, temp_values, coeffs

    @staticmethod
    def read_matrix(model_data: List[str]) -> List[Tuple]:
        """
        Read a matrix from a list of strings.

        Iterate through a provided list of strings and extract, if present, a valid matrix element
        label and any subsequent floating point values.

        Parameters
        ----------
        model_data: List[str]
            Matrix coefficient section from the output of a `TBLIST` command. Any rows that do
            not begin with a label are ignored. otherwise, each row is deserialized into a tuple
            with the string label and any associated float values.
        """
        values = []
        for row in model_data:
            label = MATRIX_LABEL_REGEX.search(row)
            if label:
                current_values = FLOAT_VALUE_REGEX.findall(row)
                values.append((label.groups()[0], *(float(value[0]) for value in current_values)))
        return values

    def write_model(self, material: "Material", pyansys_session: Any) -> None:
        """
        Write the model to MAPDL.

        This method performs some pre-flight verification and writes the correct model for the
        provided values of coefficients and temperatures.

        If no temperature value is specified for the model, the current reference temperature
        for the material is used.

        Parameters
        ----------
        pyansys_session: _MapdlCore
            Configured instance of PyMAPDL.
        material: Material
            Material object to associate with this model.
        """
        if not isinstance(pyansys_session, _MapdlCore):
            raise TypeError(
                "This model is only supported by MAPDL and Fluent. Ensure that you have the correct"
                "type of the PyAnsys session."
            )

        is_ok, issues = self.validate_model()
        if not is_ok:
            raise ModelValidationException("\n".join(issues))

        if self._temperature is None:
            self._temperature = np.array(material.reference_temperature, dtype=float)

        if self._temperature.size == 1:
            # Write ELASTIC model
            ntemp = 1
            lab = "ELASTIC"
            if self._coefficient_type == ElasticityMode.STIFFNESS:
                tbopt = "AELS"
            else:
                tbopt = "AELF"
            if len(self._coefficients.shape) != 3:
                self._coefficients = np.expand_dims(self._coefficients, 0)
        else:
            # Write ANEL model
            ntemp = self._temperature.size
            lab = "ANEL"
            if self._coefficient_type == ElasticityMode.STIFFNESS:
                tbopt = "0"
            else:
                tbopt = "1"

            # Ensure temperatures and coefficients are sorted
            sort_order = np.argsort(self._temperature)
            self._temperature = self._temperature[sort_order]
            self._coefficients = self._coefficients[sort_order, :, :]

        # Write table specification
        pyansys_session.tb(lab, material.material_id, ntemp, tbopt=tbopt)

        for temp_index, temp_val in enumerate(self._temperature):
            pyansys_session.tbtemp(temp_val)
            for chunk_index, data_chunk in enumerate(
                _chunk_lower_triangular_matrix(self._coefficients[temp_index])
            ):
                pyansys_session.tbdata(6 * chunk_index + 1, *data_chunk)

    def validate_model(self) -> Tuple[bool, List[str]]:
        """
        Validate some aspects of the model before attempting to write to MAPDL.

        This method performs these actions:

        * Validates that the number of provided temperatures match the size of the first dimension
           of the coefficient array.
        * Validates that the coefficient array is either two or three dimensional.
        * Validates that no more than six temperature samples are provided.

        Returns
        -------
        Tuple
            First element is Boolean. ``True`` if validation is successful. If ``False``,
            the second element contains a list of strings with more information.
        """
        coefficient_shape = self._coefficients.shape
        coef_matrix_count = None
        validation_errors = []
        is_valid = True

        if len(coefficient_shape) == 2:
            coef_matrix_count = 1
        elif len(coefficient_shape) == 3:
            coef_matrix_count = coefficient_shape[0]
        else:
            is_valid = False
            validation_errors.append("Invalid dimension of coefficients array. It must be 2 or 3.")

        # Check that size of temperature matches 3rd dimension of coefficients
        if coef_matrix_count and coef_matrix_count != self._temperature.size:
            is_valid = False
            validation_errors.append(
                f"Inconsistent number of temperature values ({self._temperature.size}) "
                f"and coefficient values ({coef_matrix_count})."
            )

        if self._temperature.size > 6:
            is_valid = False
            validation_errors.append("This model supports a maximum of six temperature values.")

        return is_valid, validation_errors
