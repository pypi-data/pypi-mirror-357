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

from typing import Any, List, Tuple

import numpy as np

from ansys.materials.manager._models._common._base import _BaseModel, _FluentCore, _MapdlCore
from ansys.materials.manager._models._common._exceptions import ModelValidationException
from ansys.materials.manager._models._common._packages import SupportedPackage
from ansys.materials.manager._models._fluent.simple_properties import (
    property_codes as fluent_property_codes,
)
from ansys.materials.manager._models._mapdl.simple_properties import (
    property_codes as mapdl_property_codes,
)
from ansys.materials.manager.util.common import _chunk_data

TYPE_CHECKING = False
if TYPE_CHECKING:
    from ansys.materials.manager.material import Material  # noqa: F401


class PiecewiseLinear(_BaseModel):
    """
    Provides the piecewise linear model for a property.

    This class represents a property as a series of sample points between which the value is
    interpolated.
    """

    applicable_packages: SupportedPackage.MAPDL | SupportedPackage.FLUENT
    _name: str
    _independent_variable: np.ndarray
    _dependent_variable: np.ndarray

    def __init__(self, name: str, x: np.ndarray, y: np.ndarray) -> None:
        """
        Create a piecewise linear model for a property.

        Ensure that the two arrays ``x`` and ``y`` are both one dimensional and have the same number
        of elements.

        This property is created in the default unit system of the solver. Ensure
        that you provide values in the correct units.

        Parameters
        ----------
        name: str
            Name of the property to model as a constant.
        x: np.ndarray
            Values of the independent variable over which to model the property.
            Ensure that these values cover the range of interest for the simulation.
        y: np.ndarray
            Values of the property sampled at the points represented by the ``x`` array.
        """
        self._name = name
        self._independent_variable = x
        self._dependent_variable = y

    @property
    def name(self) -> str:
        """Name of the quantity modeled by the constant."""
        return self._name

    @property
    def x(self) -> np.ndarray:
        """Values of the ``x`` array."""
        return self._independent_variable

    @x.setter
    def x(self, value: np.ndarray) -> None:
        self._independent_variable = value

    @property
    def y(self) -> np.ndarray:
        """Values of the ``y`` array."""
        return self._dependent_variable

    @y.setter
    def y(self, value: np.ndarray) -> None:
        self._dependent_variable = value

    def write_model(self, material: "Material", pyansys_session: Any) -> None:
        """
        Write the model to MAPDL.

        This method should make some effort to validate the model state before writing.

        Parameters
        ----------
        material: Material
            Material object to associate with this model.
        pyansys_session: Any
            Configured instance of the PyAnsys session.
        """
        is_ok, issues = self.validate_model()
        if not is_ok:
            raise ModelValidationException("\n".join(issues))

        if isinstance(pyansys_session, _MapdlCore):
            self._write_mapdl(pyansys_session, material)
        elif isinstance(pyansys_session, _FluentCore):
            self._write_fluent(pyansys_session, material)
        else:
            raise TypeError(
                "This model is only supported by MAPDL and Fluent. Ensure that you have the correct"
                "type of the PyAnsys session."
            )

    def _write_mapdl(self, mapdl: "_MapdlCore", material: "Material") -> None:
        if self._independent_variable.size > 100:
            raise ValueError(
                f"MAPDL supports up to 100 points for a property. "
                f"You provided {self._independent_variable.size}."
            )
        mapdl_property_code = mapdl_property_codes[self._name.lower()]
        temp_values = self._independent_variable
        for index, chunk in enumerate(_chunk_data(temp_values)):
            mapdl.mptemp(6 * index + 1, *chunk)
        property_values = self._dependent_variable
        for index, chunk in enumerate(_chunk_data(property_values)):
            mapdl.mpdata(mapdl_property_code, material.material_id, 6 * index + 1, *chunk)

    def _write_fluent(self, fluent: "_FluentCore", material: "Material") -> None:
        fluent_property_code = fluent_property_codes[self._name.lower()]
        pass

    def validate_model(self) -> "Tuple[bool, List[str]]":
        """
        Perform pre-flight validation of the model setup.

        Returns
        -------
        Tuple
            First element is Boolean. ``True`` if validation is successful. If ``False``,
            the second element contains a list of strings with more information.
        """
        failures = []
        is_ok = True

        if self._name is None or self._name == "":
            failures.append("Invalid property name")
            is_ok = False
        if self._independent_variable is None or self._independent_variable.size == 0:
            failures.append("x_values is empty. Provide at least one value.")
            is_ok = False
        if self._dependent_variable is None or self._dependent_variable.size == 0:
            failures.append("y_values is empty. Provide at least one value.")
            is_ok = False
        if not is_ok:
            return is_ok, failures
        if self._independent_variable.size != self._dependent_variable.size:
            failures.append(
                "Length mismatch. x_values and y_values must have the same number of elements."
            )
            is_ok = False
        if self._independent_variable.ndim > 1:
            failures.append(
                f"x_values must have one dimension, not {self._independent_variable.ndim}."
            )
            is_ok = False
        if self._dependent_variable.ndim > 1:
            failures.append(
                f"y_values must have one dimension, not {self._dependent_variable.ndim}."
            )
            is_ok = False
        return is_ok, failures
