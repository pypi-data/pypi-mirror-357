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

"""Provides the ``MaterialManager`` class."""

import inspect
from typing import Any, Dict

import ansys.materials.manager._models as models
from ansys.materials.manager._models._common._base import _FluentCore, _MapdlCore

from .material import Material
from .util.mapdl.mapdl_reader import read_mapdl


class MaterialManager:
    """
    Manage material creation, assignment, and other management tasks.

    This class is the main entry point for the Pythonic material management interface.
    """

    model_type_map: Dict[str, models._BaseModel] = {}
    _client: Any

    def __init__(self, pyansys_client: Any):
        """
        Create a ``MaterialManager`` object ready for use.

        Parameters
        ----------
        pyansys_client : Any
            Valid instance of a PyAnsys client. Only PyMAPDL and PyFluent are
            supported currently.
        """
        self._client = pyansys_client
        # response = inspect.getmembers(models, self.__is_subclass_predicate)
        # model_classes: List[models._BaseModel] = [tple[1] for tple in response]
        # for class_ in model_classes:
        #     supported_model_codes = class_.model_codes
        #     for model_code in supported_model_codes:
        #         self.model_type_map[model_code] = class_

    @staticmethod
    def __is_subclass_predicate(obj: object) -> bool:
        """
        Determine if an object is a strict subclass of the :obj:`models._BaseModel` class.

        Parameters
        ----------
        obj : object
            Any Python object.

        Returns
        -------
        bool
            ``True`` if the object is strictly a subclass of the :obj:`models._BaseModel`
            class, ``False`` otherwise.
        """
        return (
            isinstance(obj, type)
            and issubclass(obj, models._BaseModel)
            and not inspect.isabstract(obj)
        )

    def write_material(self, material: Material) -> None:
        """
        Write a material to the solver.

        Parameters
        ----------
        material : Material
            Material object to write to solver.
        """
        for model in material.models:
            assert isinstance(model, models._BaseModel)
            model.write_model(material, self._client)

    def read_materials_from_session(self) -> Dict[str, Material]:
        """
        Given a PyAnsys session, return the materials present.

        This method only supports PyMAPDL currently.

        Returns
        -------
        Dict[str, Material]
            Materials in the current session, indexed by an ID. For MAPDL, this is the material
            ID. For Fluent, this is the material name.
        """
        if isinstance(self._client, _MapdlCore):
            return self._read_mapdl()
        elif isinstance(self._client, _FluentCore):
            return self._read_fluent()

    def _read_mapdl(self) -> Dict[str, Material]:
        return read_mapdl(self._client)

    def _read_fluent(self) -> Dict[str, Material]:
        return []
