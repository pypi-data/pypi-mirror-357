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

from abc import ABCMeta, abstractmethod
from typing import Any, List, Tuple

try:
    from ansys.mapdl.core.mapdl import MapdlBase as _MapdlCore
except ImportError:
    try:
        from ansys.mapdl.core.mapdl import _MapdlCore
    except ImportError:
        _MapdlCore = type(None)

try:
    from ansys.fluent.core.session_solver import Solver as _FluentCore
except ImportError:
    _FluentCore = type(None)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from ansys.materials.manager._models._common._packages import SupportedPackage  # noqa: F401
    from ansys.materials.manager.material import Material  # noqa: F401


class _BaseModel(metaclass=ABCMeta):
    """
    Provides the base class that all nonlinear material models must inherit from.

    This class allows the Material Manager to dynamically discover available models and to dispatch
    deserialization calls to the appropriate model class.
    """

    applicable_packages: "SupportedPackage"

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the model.

        For complex nonlinear models, this is the name of the model. For simple models, this
        can be set and should reflect the property being modeled.
        """
        ...

    @abstractmethod
    def write_model(self, material: "Material", pyansys_session: Any) -> None:
        """
        Write the model to MAPDL.

        This method should make some effort to validate the model state before writing.

        Parameters
        ----------
        material: Material
            Material object to associate this model with.
        pyansys_session: Any
            Supported PyAnsys product session. Only PyMAPDL and PyFluent are
            supported currently.
        """
        ...

    @abstractmethod
    def validate_model(self) -> "Tuple[bool, List[str]]":
        """
        Perform pre-flight validation of the model setup.

        This method should not perform any calls to the MAPDL process.

        Returns
        -------
        Tuple
            First element is Boolean. ``True`` if validation is successful. If ``False``,
            the second element contains a list of strings with more information.
        """
        ...
