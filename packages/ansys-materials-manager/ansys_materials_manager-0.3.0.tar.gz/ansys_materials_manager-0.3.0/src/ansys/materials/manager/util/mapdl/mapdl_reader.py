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

"""Provides the ``mapdl_reader`` module."""

from typing import Dict

from ansys.materials.manager._models._common._base import _MapdlCore
from ansys.materials.manager.material import Material

from .mpdata_parser import MP_MATERIAL_HEADER_REGEX, _MaterialDataParser


def read_mapdl(mapdl: _MapdlCore) -> Dict[str, Material]:
    """
    Read materials from a provided MAPDL session.

    Returns them indexed by the material ID.

    Parameters
    ----------
    mapdl : _MapdlCore
        Active pyMAPDL session.

    Returns
    -------
    Dict[str, Material]
        Materials currently active in the MAPDL session, indexed by their material ID.
    """
    materials = []
    data = mapdl.mplist()
    material_ids = list(MP_MATERIAL_HEADER_REGEX.findall(data))
    for material_id in material_ids:
        material_properties = _MaterialDataParser.parse_material(data, int(material_id))
        materials.append(Material("", material_id, models=material_properties))
    return {
        material.material_id: material for material in materials if material.material_id is not None
    }
