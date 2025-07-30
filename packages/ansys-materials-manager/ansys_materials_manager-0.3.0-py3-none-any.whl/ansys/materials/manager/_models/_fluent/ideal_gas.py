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

from ansys.materials.manager._models import ModelValidationException, _BaseModel
from ansys.materials.manager._models._common._base import _FluentCore
from ansys.materials.manager._models._common._packages import SupportedPackage
from ansys.materials.manager._models._fluent.simple_properties import (
    property_codes as fluent_property_codes,
)
from ansys.materials.manager.material import Material


class IdealGas(_BaseModel):
    r"""
    Provides for creating an ideal gas model for fluid properties.

    This model can be applied to density and specific heat capacity properties within Fluent.
    It requires that the molar mass be set as a property and models the following equation:

    .. math::

     P * V = \frac{m * R * T}{M}
    """

    applicable_packages = SupportedPackage.FLUENT
    _name: str

    def __init__(self, name: str):
        """Create an ideal gas model for the Fluent solver."""
        self._name = name

    @property
    def name(self) -> str:
        """Name of the property modeled."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def write_model(self, material: "Material", pyansys_session: Any) -> None:
        """
        Write this model to Fluent.

        This method should make some effort to validate the model state before writing.

        Parameters
        ----------
        material: Material
            Material object to associate with this model.
        pyansys_session: Any
            Configured instance of the PyAnsys session.
        """
        if not isinstance(pyansys_session, _FluentCore):
            raise TypeError(
                "This model is only supported by MAPDL and Fluent. Ensure that you have the correct"
                "type of the PyAnsys session."
            )

        is_ok, issues = self.validate_model()

        molar_mass_prop = material.get_model_by_name("molar mass")
        if len(molar_mass_prop) == 0:
            is_ok = False
            issues.append("Molar mass must be provided for the ideal gas model.")
        if not is_ok:
            raise ModelValidationException("\n".join(issues))

        fluent_property_code = fluent_property_codes[self._name.lower()]
        pyansys_session.settings.setup.materials.fluid[material.name] = {
            fluent_property_code: {"option": "ideal-gas"}
        }

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

        return is_ok, failures
