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

"""Define a map between MAPDL and MATLM material properties."""

# todo: add more property sets and parameters to the map

# either define properties or mappings, but not both
MATML_PROPERTY_MAP = {
    "Density": {"properties": ["Density"], "mappings": {}},
    "Elasticity::Isotropic": {
        "properties": [],
        "mappings": {
            "Young's Modulus": [
                "Young's Modulus X direction",
                "Young's Modulus Y direction",
                "Young's Modulus Z direction",
            ],
            "Shear Modulus": [
                "Shear Modulus XY",
                "Shear Modulus XZ",
                "Shear Modulus YZ",
            ],
            "Poisson's Ratio": [
                "Poisson's Ratio XY",
                "Poisson's Ratio XZ",
                "Poisson's Ratio YZ",
            ],
        },
    },
    "Elasticity::Orthotropic": {
        "properties": [
            "Young's Modulus X direction",
            "Young's Modulus Y direction",
            "Young's Modulus Z direction",
            "Shear Modulus XY",
            "Shear Modulus XZ",
            "Shear Modulus YZ",
            "Poisson's Ratio XY",
            "Poisson's Ratio XZ",
            "Poisson's Ratio YZ",
        ],
        "mappings": {},
    },
    "Coefficient of Thermal Expansion::Isotropic::Secant": {
        "properties": [],
        "mappings": {
            "Coefficient of Thermal Expansion": [
                "secant thermal expansion coefficient x direction",
                "secant thermal expansion coefficient y direction",
                "secant thermal expansion coefficient z direction",
            ]
        },
    },
    "Coefficient of Thermal Expansion::Isotropic::Instantaneous": {
        "properties": [],
        "mappings": {
            "Coefficient of Thermal Expansion": [
                "instantaneous thermal expansion coefficient x direction",
                "instantaneous thermal expansion coefficient y direction",
                "instantaneous thermal expansion coefficient z direction",
            ]
        },
    },
    "Coefficient of Thermal Expansion::Orthotropic::Secant": {
        "properties": [],
        "mappings": {
            "Coefficient of Thermal Expansion X direction": [
                "secant thermal expansion coefficient x direction"
            ],
            "Coefficient of Thermal Expansion Y direction": [
                "secant thermal expansion coefficient y direction"
            ],
            "Coefficient of Thermal Expansion Z direction": [
                "secant thermal expansion coefficient z direction"
            ],
        },
    },
    "Coefficient of Thermal Expansion::Orthotropic::Instantaneous": {
        "properties": [],
        "mappings": {
            "Coefficient of Thermal Expansion X direction": [
                "instantaneous thermal expansion coefficient x direction"
            ],
            "Coefficient of Thermal Expansion Y direction": [
                "instantaneous thermal expansion coefficient y direction"
            ],
            "Coefficient of Thermal Expansion Z direction": [
                "instantaneous thermal expansion coefficient z direction"
            ],
        },
    },
    "Specific Heat": {"properties": [], "mappings": {"Specific Heat": ["Specific Heat Capacity"]}},
    "Thermal Conductivity::Isotropic": {
        "properties": [],
        "mappings": {
            "Thermal Conductivity": [
                "Thermal Conductivity X direction",
                "Thermal Conductivity Y direction",
                "Thermal Conductivity Z direction",
            ]
        },
    },
    "Thermal Conductivity::Orthotropic": {
        "properties": [
            "Thermal Conductivity X direction",
            "Thermal Conductivity Y direction",
            "Thermal Conductivity Z direction",
        ],
        "mappings": {},
    },
    "Viscosity": {"properties": ["Viscosity"], "mappings": {}},
    "Speed of Sound": {"properties": ["Speed of Sound"], "mappings": {}},
}
