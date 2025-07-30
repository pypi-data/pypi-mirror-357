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

"""Provides the ``MaterialDataParser`` class."""

from typing import Dict, List, Optional

import numpy as np

from ansys.materials.manager._models import Constant, PiecewiseLinear, _BaseModel
from ansys.materials.manager._models._mapdl.simple_properties import property_codes
from ansys.materials.manager.util.common import FLOAT_VALUE_REGEX, MP_MATERIAL_HEADER_REGEX


class _MaterialDataParser:
    @staticmethod
    def parse_material(data: str, id_: int) -> List[_BaseModel]:
        """
        Parse the response from an `MPLIST` command.

        Creates a list of material models applied to the material.

        Parameters
        ----------
        data : str
            String response from the `MPLIST` command.
        id_ : int
            Material identity to be parsed.

        Returns
        -------
        List[_BaseModel]
            List of models assigned to this material.
        """
        data_section = _MaterialDataParser._get_mp_section_with_id(data, id_)
        return _MaterialDataParser._process_material(data_section)

    @staticmethod
    def _get_mp_section_with_id(data: str, id_: int) -> List[str]:
        """
        Extract material property information for the specified material identity.

        Parameters
        ----------
        data : str
            String response from the `MPLIST` command.
        id_ : int
            Material identity to be extracted.

        Returns
        -------
        List[str]
            Relevant section of the data input, split on newlines.
        """
        material_ids = map(int, MP_MATERIAL_HEADER_REGEX.findall(data))
        if id_ not in material_ids:
            raise IndexError(f"Material with ID {id_} not found in data")

        relevant_lines = []
        reading_correct_material = False
        for line in data.splitlines():
            stripped_line = line.strip()
            if stripped_line.startswith("MATERIAL"):
                match = MP_MATERIAL_HEADER_REGEX.match(stripped_line)
                if match:
                    current_id = int(match.groups()[0])
                    if current_id == id_:
                        reading_correct_material = True
                    else:
                        reading_correct_material = False
            elif reading_correct_material:
                relevant_lines.append(line)

        return relevant_lines

    @staticmethod
    def _process_material(material_data: List[str]) -> List[_BaseModel]:
        """
        Deserialize a material into a list of material models.

        Parameters
        ----------
        material_data : List[str]
            List of lines containing property data for one material.

        Returns
        -------
        List[_BaseModel]
            List of models applied to this material.
        """
        property_data: List[_BaseModel] = []
        property_lines: Dict[str, List[str]] = {}
        reference_temperature = None
        current_property_code = None
        lines = [line.strip() for line in material_data if line.strip()]
        for line in lines:
            if line.startswith("TEMP"):
                current_property_code = _MaterialDataParser._process_property_header(line)
                property_lines[current_property_code] = []
            elif line.startswith("REFT"):
                temp_string = line.split("=")[1]
                temp_val_match = FLOAT_VALUE_REGEX.search(temp_string)
                assert temp_val_match is not None, "Invalid material input"
                reference_temperature = float(temp_val_match.group(0))
            else:
                assert current_property_code is not None, "Invalid material input"
                property_lines[current_property_code].append(line)
        for name, value in property_lines.items():
            property_data.append(_MaterialDataParser._process_property(name, value))
        if reference_temperature is not None:
            property_data.append(Constant("Strain Reference Temperature", reference_temperature))
        return property_data

    @staticmethod
    def _process_property_header(header_line: str) -> str:
        """
        Deserialize a property header line into the relevant named property.

        Parameters
        ----------
        header_line : str
            Material property header line.

        Returns
        -------
        str
            Corresponding standard name for the property.

        Raises
        ------
        KeyError
            If the header line specifies an unknown property.
        IndexError
            If the header line does not match the expected format.
        """
        stripped_header_line = header_line.strip()
        try:
            property_name = stripped_header_line[4:].strip().split(" ")[0]
        except IndexError:
            raise IndexError("Invalid property header line")
        try:
            return next(k for k, v in property_codes.items() if v == property_name.upper())
        except StopIteration:
            raise KeyError(f"Invalid property: '{property_name}'")

    @staticmethod
    def _process_property(property_name: str, property_data: List[str]) -> _BaseModel:
        """
        Deserialize the property data into a model representing the property.

        Single values are deserialized into Constant models, arrays are deserialized
        into PiecewiseLinear models.

        Parameters
        ----------
        property_name : str
            Name of the property to be deserialized.
        property_data : List[str]
            Property data section to be deserialized.

        Returns
        -------
        _BaseModel
            Deserialized model, either a Constant or PiecewiseLinear model at this point.
        """
        model: Optional[_BaseModel] = None
        if len(property_data) == 1:
            match = FLOAT_VALUE_REGEX.search(property_data[0])
            if match:
                property_value = float(match.group(0))
                model = Constant(property_name, property_value)
        else:
            property_value = []
            parameter_value = []
            for data_line in property_data:
                line_values = FLOAT_VALUE_REGEX.findall(data_line)
                parameter_value.append(float(line_values[0][0]))
                property_value.append(float(line_values[1][0]))
            model = PiecewiseLinear(
                property_name, x=np.array(parameter_value), y=np.array(property_value)
            )

        assert model is not None, "Invalid property data input"
        return model
