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

"""Provides a function to convert MatML entries into Material objects."""

from typing import Dict, Sequence

from ansys.materials.manager._models import Constant
from ansys.materials.manager.material import Material
from ansys.materials.manager.util.matml.matml_property_map import MATML_PROPERTY_MAP


def convert_matml_materials(
    materials_dict: Dict, transfer_ids: Dict, index_offset: int
) -> Sequence[Material]:
    """
    Convert a list of materials into Material objects.

    Parameters
    ----------
    materials_dict:
        dict of raw material data from a matml import
    transfer_ids:
        dict of material names and unique transfer ids
    index_offset:
        int to offset the material id (number) to avoid conflicts with already existing materials
    Returns a list of Material objects
    """
    materials = []

    global_material_index = 1 + index_offset
    # loop over the materials
    for mat_id, material_data in materials_dict.items():

        models = []
        # loop over the defined property sets
        for propset_name, property_set in material_data.items():

            if "Behavior" in property_set.qualifiers.keys():
                propset_name += "::" + property_set.qualifiers["Behavior"]

            if "Definition" in property_set.qualifiers.keys() and propset_name.startswith(
                "Coefficient of Thermal Expansion"
            ):
                propset_name += "::" + property_set.qualifiers["Definition"]

            # check if the Material object supports this property set
            if propset_name in MATML_PROPERTY_MAP.keys():
                parameter_map = MATML_PROPERTY_MAP[propset_name]

                for property_name in parameter_map["properties"]:
                    param = property_set.parameters[property_name]
                    value = param.data
                    if isinstance(value, Sequence):
                        if len(value) > 1:
                            raise RuntimeError(
                                f"Only constant material properties are supported ATM. "
                                f"Value of `{property_name}` is `{value}`"
                            )
                        value = value[0]
                    models.append(Constant(property_name, value))
                for matml_key, mapped_properties in parameter_map["mappings"].items():
                    param = property_set.parameters[matml_key]
                    value = param.data
                    if isinstance(value, Sequence):
                        if len(value) > 1:
                            raise RuntimeError(
                                f"Only constant material properties are supported ATM. "
                                f"Value of `{matml_key}` is `{value}`"
                            )
                        value = value[0]
                    for mapped_property in mapped_properties:
                        models.append(Constant(mapped_property, value))

        mapdl_material = Material(
            material_name=mat_id, material_id=global_material_index, models=models
        )

        if mat_id in transfer_ids.keys():
            mapdl_material.uuid = transfer_ids[mat_id]

        materials.append(mapdl_material)

        global_material_index += 1

    return materials
