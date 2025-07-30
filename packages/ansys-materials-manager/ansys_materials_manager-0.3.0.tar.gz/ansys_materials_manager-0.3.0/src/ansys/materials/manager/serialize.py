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

"""Provides functions to serialize materials."""

import json
import pathlib
from typing import Dict, Union

from ansys.materials.manager._models import Constant
from ansys.materials.manager.material import Material


def _material_as_dict(material: Material) -> Dict:
    d = {"name": material.name}
    if material.material_id is not None:
        d.update({"id": material.material_id})
    for model in material.models:
        if isinstance(model, Constant):
            propData = {"option": "constant", "value": model.value}
        else:
            propData = {"option": "ideal_gas"}
        d.update({model.name: propData})
    return d


def serialize_material(material: Material) -> str:
    """
    Output the JSON representation of a material in Fluent format to a string.

    Parameters
    ----------
    material : Material
        Material to serialize.

    Returns
    -------
    str
        String representation of the material in Fluent format.
    """
    d = _material_as_dict(material)
    return json.dumps(d)


def serialize_material_to_file(material: Material, file_name: Union[str, pathlib.Path]):
    """
    Output the JSON representation of a material in Fluent format to a file.

    Parameters
    ----------
    material : Material
        Material to serialize.
    file_name : Union[str, pathlib.Path]
        Name of the file to create.
    """
    sm = serialize_material(material)
    with open(file_name, "w", encoding="utf8") as f:
        f.write(sm)
