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

"""Provides the ``common`` module."""

from itertools import islice
import re
from typing import Generator, Iterable, List, Union

import numpy as np

MP_MATERIAL_HEADER_REGEX = re.compile(r"MATERIAL NUMBER\s+([\d]+)")
TB_MATERIAL_HEADER_REGEX = re.compile(r"\(([A-Z]+)\) Table For Material\s+([\d]+)[^\n]*")
FLOAT_VALUE_REGEX = re.compile(r"(-?\d+\.\d*([Ee][+-]\d+)?)")
INTEGER_VALUE_REGEX = re.compile(r"(-?\d+)")
MATRIX_LABEL_REGEX = re.compile(r"(\w\s?\d{1,2})")

model_type = Union[float, np.ndarray]


def _chunk_data(data: Iterable) -> Generator[List, None, None]:
    """
    Split an iterable into chunks of size six lazily.

    Parameters
    ----------
    data : Iterable
        Input data.

    Returns
    -------
    Generator[List]
        Generator that will return the input data in lists of length 6 or less.
    """
    data_iterator = iter(data)
    piece = list(islice(data_iterator, 6))
    while piece:
        yield piece
        piece = list(islice(data_iterator, 6))


def _chunk_lower_triangular_matrix(
    matrix: np.ndarray,
) -> Generator[Iterable[float], None, None]:
    """
    Convert a lower-triangular square matrix into a chunked vector.

    This is intended for use with symmetric matrices, where the upper half can be ignored.

    Parameters
    ----------
    matrix : np.ndarray
        Input square matrix.

    Returns
    -------
    Generator[Iterable[float]]
        Chunked vector with coefficients in the lower half-matrix. E.g. D11, D12, D22, etc.

    Notes
    -----
    If the input matrix is non-symmetric then the upper half-matrix will be lost.
    """
    vals = []
    if np.ndim(matrix) != 2:
        raise ValueError("Input matrix must be two dimensional.")
    size = matrix.shape
    if size[0] != size[1]:
        raise ValueError("Input matrix must be square.")
    for col_index in range(0, matrix.shape[1]):
        for row_index in range(col_index, matrix.shape[0]):
            vals.append(matrix[row_index][col_index])
    return _chunk_data(vals)


def fill_upper_triangular_matrix(vector: List[float]) -> np.ndarray:
    """
    Convert a vector of coefficients into a full matrix.

    Generates a symmetric, square matrix.

    Parameters
    ----------
    vector : List[float]
        Coefficients of the lower half-matrix. E.g. D11, D12, D22, etc.

    Returns
    -------
    np.ndarray
        Square symmetric matrix.

    Raises
    ------
    ValueError
        If the length of the input vector is not a triangular number.
    """
    size_x = (np.sqrt(8 * len(vector) + 1) - 1) / 2
    if not np.isclose(int(size_x), size_x):
        raise ValueError(
            f"vector does not appear to be a valid lower-triangular matrix in flat form "
            f"(size {len(vector)}) is not a triangular number"
        )
    size_x = int(size_x)
    output = np.zeros((size_x, size_x))
    output[np.triu_indices(output.shape[0], k=0)] = vector
    return output + output.T - np.diag(np.diag(output))
