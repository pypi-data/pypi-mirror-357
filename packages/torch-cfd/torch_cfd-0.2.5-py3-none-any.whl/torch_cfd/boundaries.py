# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modifications copyright (C) 2025 S.Cao
# ported Google's Jax-CFD functional template to PyTorch's tensor ops


import dataclasses
import math
from typing import Callable, List, Optional, Sequence, Tuple, Union

import torch

from torch_cfd import grids

BoundaryConditions = grids.BoundaryConditions
Grid = grids.Grid
GridVariable = grids.GridVariable
GridVariableVector = grids.GridVariableVector


BCType = grids.BCType()
Padding = grids.Padding()
BCValues = grids.BCValues


@dataclasses.dataclass(init=False, frozen=True, repr=False)
class ConstantBoundaryConditions(BoundaryConditions):
    """Boundary conditions for a PDE variable that are constant in space and time.

    Attributes:
        types: a tuple of tuples, where `types[i]` is a tuple specifying the lower and upper BC types for dimension `i`. The types can be one of the following:
            BCType.PERIODIC, BCType.DIRICHLET, BCType.NEUMANN.
        values: a tuple of tuples, where `values[i]` is a tuple specifying the lower and upper boundary values for dimension `i`. If None, the boundary condition is homogeneous (zero).

    Example usage:
      grid = Grid((10, 10))
      bc = ConstantBoundaryConditions(((BCType.PERIODIC, BCType.PERIODIC),
                                          (BCType.DIRICHLET, BCType.DIRICHLET)),
                                          ((0.0, 10.0),(1.0, 0.0)))
      # in dimension 0 is periodic, (0, 10) on left and right (un-used)
      # in dimension 1 is dirichlet, (1, 0) on bottom and top.
      v = GridVariable(torch.zeros((10, 10)), offset=(0.5, 0.5), grid, bc)
      # v.offset is (0.5, 0.5) which is the cell center, so the boundary conditions have no effect in this case

    """

    _types: Tuple[Tuple[str, str], ...]
    bc_values: Tuple[Tuple[Optional[float], Optional[float]], ...]
    ndim: int

    def __init__(
        self,
        types: Sequence[Tuple[str, str]],
        values: Sequence[Tuple[Optional[float], Optional[float]]],
    ):
        types = tuple(types)
        values = tuple(values)
        object.__setattr__(self, "_types", types)
        object.__setattr__(self, "bc_values", values)
        object.__setattr__(self, "ndim", len(types))

    @property
    def types(self) -> Tuple[Tuple[str, str], ...]:
        """Returns the boundary condition types."""
        return self._types

    @types.setter
    def types(self, bc_types: Sequence[Tuple[str, str]]) -> None:
        """Sets the boundary condition types and updates ndim accordingly."""
        bc_types = tuple(bc_types)
        assert self.ndim == len(
            bc_types
        ), f"Number of dimensions {self.ndim} does not match the number of types {bc_types}."
        object.__setattr__(self, "_types", bc_types)

    def __repr__(self) -> str:
        try:
            lines = [f"{self.__class__.__name__}({self.ndim}D):"]

            for dim in range(self.ndim):
                lower_type, upper_type = self.types[dim]
                lower_val, upper_val = self.bc_values[dim]

                # Format values
                lower_val_str = "None" if lower_val is None else f"{lower_val}"
                upper_val_str = "None" if upper_val is None else f"{upper_val}"

                lines.append(
                    f"  dim {dim}: [{lower_type}({lower_val_str}), {upper_type}({upper_val_str})]"
                )

            return "\n".join(lines)
        except Exception as e:
            return f"{self.__class__.__name__} not initialized: {e}"

    def clone(
        self,
        types: Optional[Sequence[Tuple[str, str]]] = None,
        values: Optional[Sequence[Tuple[Optional[float], Optional[float]]]] = None,
    ) -> BoundaryConditions:
        """Creates a copy of this boundary condition, optionally with modified parameters.

        Args:
            types: New boundary condition types. If None, uses current types.
            values: New boundary condition values. If None, uses current values.

        Returns:
            A new ConstantBoundaryConditions instance.
        """
        new_types = types if types is not None else self.types
        new_values = values if values is not None else self.bc_values
        return ConstantBoundaryConditions(new_types, new_values)

    def shift(
        self,
        u: GridVariable,
        offset: int,
        dim: int,
    ) -> GridVariable:
        """
        A fallback function to make the implementation back-compatible
        see grids.shift
        bc.shift(u, offset, dim) overrides u.bc
        grids.shift(u, offset, dim) keeps u.bc
        """
        return grids.shift(u, offset, dim, self)

    def _is_aligned(self, u: GridVariable, dim: int) -> bool:
        """Checks if array u contains all interior domain information.

        For dirichlet edge aligned boundary, the value that lies exactly on the
        boundary does not have to be specified by u.
        Neumann edge aligned boundary is not defined.

        Args:
        u: GridVariable that should contain interior data
        dim: axis along which to check

        Returns:
        True if u is aligned, and raises error otherwise.
        """
        size_diff = u.shape[dim] - u.grid.shape[dim]
        if self.types[dim][0] == BCType.DIRICHLET and math.isclose(u.offset[dim], 1):
            size_diff += 1
        if self.types[dim][1] == BCType.DIRICHLET and math.isclose(u.offset[dim], 1):
            size_diff += 1
        if (
            self.types[dim][0] == BCType.NEUMANN and math.isclose(u.offset[dim], 1)
        ) or (self.types[dim][1] == BCType.NEUMANN and math.isclose(u.offset[dim], 0)):
            """
            if lower (or left for dim 0) is Neumann, and the offset is 1 (the variable is on the right edge of a cell), the Neumann bc is not defined; vice versa for upper (or right for dim 0) Neumann bc with offset 0 (the variable is on the left edge of a cell).
            """
            raise ValueError("Variable not aligned with Neumann BC")
        if size_diff < 0:
            raise ValueError(
                "the GridVariable does not contain all interior grid values."
            )
        return True

    def pad(
        self,
        u: GridVariable,
        width: Union[Tuple[int, int], int],
        dim: int,
        mode: Optional[str] = Padding.EXTEND,
    ) -> GridVariable:
        """Wrapper for grids.pad with a specific bc.

        Args:
          u: a `GridVariable` object.
          width: number of elements to pad along axis. If width is an int, use
            negative value for lower boundary or positive value for upper boundary.
            If a tuple, pads with width[0] on the left and width[1] on the right.
          dim: axis to pad along.
          mode: type of padding to use in non-periodic case.
            Mirror mirrors the array values across the boundary.
            Extend extends the last well-defined array value past the boundary.

        Returns:
          Padded array, elongated along the indicated axis.
          the original u.bc will be replaced with self.
        """
        _ = self._is_aligned(u, dim)
        if isinstance(width, tuple) and (width[0] > 0 and width[1] > 0):
            need_trimming = "both"
        elif (isinstance(width, tuple) and (width[0] > 0 and width[1] == 0)) or (
            isinstance(width, int) and width < 0
        ):
            need_trimming = "left"
        elif (isinstance(width, tuple) and (width[0] == 0 and width[1] > 0)) or (
            isinstance(width, int) and width > 0
        ):
            need_trimming = "right"
        else:
            need_trimming = "none"

        u, trimmed_padding = self._trim_padding(u, dim, need_trimming)

        if isinstance(width, int):
            if width < 0:
                width -= trimmed_padding[0]
            if width > 0:
                width += trimmed_padding[1]
        elif isinstance(width, tuple):
            width = (width[0] + trimmed_padding[0], width[1] + trimmed_padding[1])

        u = grids.pad(u, width, dim, self, mode=mode)
        return u

    def pad_all(
        self,
        u: GridVariable,
        width: Tuple[Tuple[int, int], ...],
        mode: Optional[str] = Padding.EXTEND,
    ) -> GridVariable:
        """Pads along all axes with pad width specified by width tuple.

        Args:
          u: a `GridVariable` object.
          width: Tuple of padding width for each side for each axis.
          mode: type of padding to use in non-periodic case.
            Mirror mirrors the array values across the boundary.
            Extend extends the last well-defined array value past the boundary.

        Returns:
          Padded array, elongated along all axes.
        """
        for dim in range(-u.grid.ndim, 0):
            u = self.pad(u, width[dim], dim, mode=mode)
        return u

    def values(
        self, dim: int, grid: Grid
    ) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor]]:
        """Returns boundary values on the grid along axis.

        Args:
          dim: axis along which to return boundary values.
          grid: a `Grid` object on which to evaluate boundary conditions.

        Returns:
          A tuple of arrays of grid.ndim - 1 dimensions that specify values on the
          boundary. In case of periodic boundaries, returns a tuple(None,None).
        """
        if None in self.bc_values[dim]:
            return (None, None)

        bc = []
        for i in [0, 1]:
            value = self.bc_values[dim][-i]
            if value is None:
                bc.append(None)
            elif isinstance(value, float):
                bc.append(torch.full(grid.shape[:dim] + grid.shape[dim + 1 :], value))
            elif isinstance(value, torch.Tensor):
                if value.shape != grid.shape[:dim] + grid.shape[dim + 1 :]:
                    raise ValueError(
                        f"Boundary value shape {value.shape} does not match expected shape {grid.shape[:dim] + grid.shape[dim + 1 :]}"
                    )
                bc.append(value)

        return tuple(bc)

    def _trim_padding(
        self, u: GridVariable, dim: int = -1, trim_side: str = "both"
    ) -> Tuple[GridVariable, Tuple[int, int]]:
        """Trims padding from a GridVariable along axis and returns the array interior.

        Args:
        u: a `GridVariable` object.
        dim: axis to trim along.
        trim_side: if 'both', trims both sides. If 'right', trims the right side.
            If 'left', the left side.

        Returns:
        Trimmed array, shrunk along the indicated axis side. bc is updated to None
        """
        positive_trim = 0
        negative_trim = 0
        padding = (0, 0)

        if trim_side not in ("both", "left", "right"):
            return u.array, padding

        if u.shape[dim] >= u.grid.shape[dim]:
            # number of cells that were padded on the left
            negative_trim = 0
            if u.offset[dim] <= 0 and (trim_side == "both" or trim_side == "left"):
                negative_trim = -math.ceil(-u.offset[dim])
                # periodic is a special case. Shifted data might still contain all the
                # information.
                if self.types[dim][0] == BCType.PERIODIC:
                    negative_trim = max(negative_trim, u.grid.shape[dim] - u.shape[dim])
                # for both DIRICHLET and NEUMANN cases the value on grid.domain[0] is
                # a dependent value.
                elif math.isclose(u.offset[dim] % 1, 0):
                    negative_trim -= 1
                u = grids.trim(u, negative_trim, dim)
            # number of cells that were padded on the right
            positive_trim = 0
            if trim_side == "right" or trim_side == "both":
                # periodic is a special case. Boundary on one side depends on the other
                # side.
                if self.types[dim][1] == BCType.PERIODIC:
                    positive_trim = max(u.shape[dim] - u.grid.shape[dim], 0)
                else:
                    # for other cases, where to trim depends only on the boundary type
                    # and data offset.
                    last_u_offset = u.shape[dim] + u.offset[dim] - 1
                    boundary_offset = u.grid.shape[dim]
                    if last_u_offset >= boundary_offset:
                        positive_trim = math.ceil(last_u_offset - boundary_offset)
                        if self.types[dim][1] == BCType.DIRICHLET and math.isclose(
                            u.offset[dim] % 1, 0
                        ):
                            positive_trim += 1
        if positive_trim > 0:
            u = grids.trim(u, positive_trim, dim)
        # combining existing padding with new padding
        padding = (-negative_trim, positive_trim)
        return u, padding

    def trim_boundary(self, u: GridVariable) -> GridVariable:
        """Returns GridVariable without the grid points on the boundary.

        Some grid points of GridVariable might coincide with boundary. This trims those values.
        If the array was padded beforehand, removes the padding.

        Args:
        u: a `GridVariable` object.

        Returns:
        A GridVariable shrunk along certain dimensions.
        """
        for dim in range(-u.grid.ndim, 0):
            _ = self._is_aligned(u, dim)
            u, _ = self._trim_padding(u, dim)
        return GridVariable(u.data, u.offset, u.grid)

    def pad_and_impose_bc(
        self,
        u: GridVariable,
        offset_to_pad_to: Optional[Tuple[float, ...]] = None,
        mode: Optional[str] = "",
    ) -> GridVariable:
        """Returns GridVariable with correct boundary values.

        Some grid points of GridVariable might coincide with boundary, thus this function is only used with the trimmed GridVariable.
        Args:
            - u: a `GridVariable` object that specifies only scalar values on the internal nodes.
            - offset_to_pad_to: a Tuple of desired offset to pad to. Note that if the function is given just an interior array in dirichlet case, it can pad to both 0 offset and 1 offset.
            - mode: type of padding to use in non-periodic case. Mirror mirrors the flow across the boundary. Extend extends the last well-defined value past the boundary. None means no ghost cell padding.

        Returns:
        A GridVariable that has correct boundary values.
        """
        assert u.bc is None, "u must be trimmed before padding and imposing bc."
        if offset_to_pad_to is None:
            offset_to_pad_to = u.offset
        for dim in range(-u.grid.ndim, 0):
            _ = self._is_aligned(u, dim)
            if self.types[dim][0] != BCType.PERIODIC:
                if mode:
                    # if the offset is either 0 or 1, u is aligned with the boundary and is defined on cell edges on one side of the boundary, if trim_boundary is called before this function.
                    # u needs to be padded on both sides
                    # if the offset is 0.5, one ghost cell is needed on each side.
                    # it will be taken care by grids.pad function automatically.
                    u = grids.pad(u, (1, 1), dim, self, mode=mode)
                elif self.types[dim][0] == BCType.DIRICHLET and not mode:
                    if math.isclose(offset_to_pad_to[dim], 1.0):
                        u = grids.pad(u, 1, dim, self)
                    elif math.isclose(offset_to_pad_to[dim], 0.0):
                        u = grids.pad(u, -1, dim, self)
                elif self.types[dim][0] == BCType.NEUMANN and not mode:
                    if not math.isclose(offset_to_pad_to[dim], 0.5):
                        raise ValueError("Neumann bc is not defined on edges.")
                else:
                    raise NotImplementedError(
                        f"Padding for {self.types[dim][0]} boundary conditions is not implemented."
                    )
        return GridVariable(u.data, u.offset, u.grid, self)

    def impose_bc(self, u: GridVariable, mode: str = "") -> GridVariable:
        """Returns GridVariable with correct boundary condition.

        Some grid points of GridVariable might coincide with boundary. This ensures
        that the GridVariable.array agrees with GridVariable.bc.
        Args:
        u: a `GridVariable` object.

        Returns:
        A GridVariable that has correct boundary values.

        Notes:
        If one needs ghost_cells, please use a manual function pad_all to add ghost cells are added on the other side of DoFs living at cell center if the bc is Dirichlet or Neumann.
        """
        offset = u.offset
        u = self.trim_boundary(u)
        u = self.pad_and_impose_bc(u, offset, mode)
        return u


class HomogeneousBoundaryConditions(ConstantBoundaryConditions):
    """Boundary conditions for a PDE variable.

    Example usage:
      grid = Grid((10, 10))
      bc = ConstantBoundaryConditions(((BCType.PERIODIC, BCType.PERIODIC),
                                          (BCType.DIRICHLET, BCType.DIRICHLET)))
      u = GridVariable(torch.zeros((10, 10)), offset=(0.5, 0.5), grid, bc)


    Attributes:
      types: `types[i]` is a tuple specifying the lower and upper BC types for
        dimension `i`.
    """

    def __init__(self, types: Sequence[Tuple[str, str]]):

        ndim = len(types)
        values = ((0.0, 0.0),) * ndim
        super(HomogeneousBoundaryConditions, self).__init__(types, values)


def is_bc_periodic_boundary_conditions(bc: BoundaryConditions, dim: int) -> bool:
    """Returns true if scalar has periodic bc along axis."""
    if bc is None:
        return False
    elif bc.types[dim][0] != BCType.PERIODIC:
        return False
    elif bc.types[dim][0] == BCType.PERIODIC and bc.types[dim][0] != bc.types[dim][1]:
        raise ValueError(
            "periodic boundary conditions must be the same on both sides of the axis"
        )
    return True


def is_bc_all_periodic_boundary_conditions(bc: BoundaryConditions) -> bool:
    """Returns true if scalar has periodic bc along all axes."""
    for dim in range(bc.ndim):
        if not is_bc_periodic_boundary_conditions(bc, dim):
            return False
    return True


def is_periodic_boundary_conditions(c: GridVariable, dim: int) -> bool:
    """Returns true if scalar has periodic bc along axis."""
    return is_bc_periodic_boundary_conditions(c.bc, dim)


def is_bc_pure_neumann_boundary_conditions(bc: BoundaryConditions) -> bool:
    """Returns true if scalar has pure Neumann bc along all axes."""
    for dim in range(bc.ndim):
        if bc.types[dim][0] != BCType.NEUMANN or bc.types[dim][1] != BCType.NEUMANN:
            return False
    return True


def is_pure_neumann_boundary_conditions(c: GridVariable) -> bool:
    """Returns true if scalar has pure Neumann bc along all axes."""
    return is_bc_pure_neumann_boundary_conditions(c.bc)


# Convenience utilities to ease updating of BoundaryConditions implementation
def periodic_boundary_conditions(ndim: int) -> BoundaryConditions:
    """Returns periodic BCs for a variable with `ndim` spatial dimension."""
    return HomogeneousBoundaryConditions(((BCType.PERIODIC, BCType.PERIODIC),) * ndim)


def dirichlet_boundary_conditions(
    ndim: int,
    bc_values: Optional[Sequence[Tuple[float, float]]] = None,
) -> BoundaryConditions:
    """Returns Dirichelt BCs for a variable with `ndim` spatial dimension.

    Args:
      ndim: spatial dimension.
      bc_vals: A tuple of lower and upper boundary values for each dimension.
        If None, returns Homogeneous BC.

    Returns:
      BoundaryCondition subclass.
    """
    if not bc_values:
        return HomogeneousBoundaryConditions(
            ((BCType.DIRICHLET, BCType.DIRICHLET),) * ndim
        )
    else:
        return ConstantBoundaryConditions(
            ((BCType.DIRICHLET, BCType.DIRICHLET),) * ndim, bc_values
        )


def neumann_boundary_conditions(
    ndim: int,
    bc_vals: Optional[Sequence[Tuple[float, float]]] = None,
) -> BoundaryConditions:
    """Returns Neumann BCs for a variable with `ndim` spatial dimension.

    Args:
      ndim: spatial dimension.
      bc_vals: A tuple of lower and upper boundary values for each dimension.
        If None, returns Homogeneous BC.

    Returns:
      BoundaryCondition subclass.
    """
    if not bc_vals:
        return HomogeneousBoundaryConditions(((BCType.NEUMANN, BCType.NEUMANN),) * ndim)
    else:
        return ConstantBoundaryConditions(
            ((BCType.NEUMANN, BCType.NEUMANN),) * ndim, bc_vals
        )


def dirichlet_and_periodic_boundary_conditions(
    bc_vals: Optional[Tuple[float, float]] = None,
) -> BoundaryConditions:
    """Returns BCs Dirichlet for dimension 0 and Periodic for dimension 1.

    Args:
      bc_vals: the lower and upper boundary condition value for each dimension. If
        None, returns Homogeneous BC.

    Returns:
      BoundaryCondition subclass.
    """
    if not bc_vals:
        return HomogeneousBoundaryConditions(
            ((BCType.DIRICHLET, BCType.DIRICHLET), (BCType.PERIODIC, BCType.PERIODIC))
        )
    else:
        return ConstantBoundaryConditions(
            ((BCType.DIRICHLET, BCType.DIRICHLET), (BCType.PERIODIC, BCType.PERIODIC)),
            (bc_vals, (None, None)),
        )


def periodic_and_neumann_boundary_conditions(
    bc_vals: Optional[Tuple[float, float]] = None,
) -> BoundaryConditions:
    """Returns BCs periodic for dimension 0 and Neumann for dimension 1.

    Args:
      bc_vals: the lower and upper boundary condition value for each dimension. If
        None, returns Homogeneous BC.

    Returns:
      BoundaryCondition subclass.
    """
    if not bc_vals:
        return HomogeneousBoundaryConditions(
            ((BCType.PERIODIC, BCType.PERIODIC), (BCType.NEUMANN, BCType.NEUMANN))
        )
    else:
        return ConstantBoundaryConditions(
            ((BCType.PERIODIC, BCType.PERIODIC), (BCType.NEUMANN, BCType.NEUMANN)),
            ((None, None), bc_vals),
        )


@dataclasses.dataclass(init=False, frozen=True, repr=False)
class DiscreteBoundaryConditions(ConstantBoundaryConditions):
    """Boundary conditions that can vary spatially along the boundary.

    Array-based values that are evaluated at boundary nodes with proper offsets. The values must match a variable's offset in order that the numerical differentiation is correct.

    Attributes:
        types: boundary condition types for each dimension
        bc_values: boundary values that can be:
            - torch.Tensor: precomputed values along boundary
            - None: homogeneous boundary condition

    Example usage:
        # Array-based boundary conditions
        grid = Grid((10, 20))
        x_boundary = torch.linspace(0, 1, 20)  # values along y-axis
        y_boundary = torch.sin(torch.linspace(0, 2*np.pi, 10))  # values along x-axis

        bc = VariableBoundaryConditions(
            types=((BCType.DIRICHLET, BCType.DIRICHLET),
                   (BCType.NEUMANN, BCType.DIRICHLET)),
            values=((y_boundary, y_boundary),  # left/right boundaries
                    (None, x_boundary))        # bottom/top boundaries
        )
    """

    _types: Tuple[Tuple[str, str], ...]
    _bc_values: Tuple[Tuple[Union[float, BCValues], Union[float, BCValues]], ...]
    ndim: int  # default 2d, dataclass init=False

    def __init__(
        self,
        types: Sequence[Tuple[str, str]],
        values: Sequence[
            Tuple[
                Union[float, BCValues],
                Union[float, BCValues],
            ]
        ],
    ):
        types = tuple(types)
        values = tuple(values)
        object.__setattr__(self, "_types", types)
        object.__setattr__(self, "_bc_values", values)
        object.__setattr__(self, "ndim", len(types))

    @property
    def has_callable(self) -> bool:
        """Check if any boundary values are callable functions."""
        for dim in range(self.ndim):
            for side in range(2):
                if callable(self._bc_values[dim][side]):
                    return True
        return False

    def _validate_boundary_arrays_with_grid(self, grid: Grid):
        """Validate boundary arrays against grid dimensions."""
        for dim in range(self.ndim):
            for side in range(2):
                value = self._bc_values[dim][side]
                if isinstance(value, torch.Tensor):
                    # Calculate expected boundary shape
                    expected_shape = grid.shape[:dim] + grid.shape[dim + 1 :]
                    if len(expected_shape) == 0:
                        # 1D case - boundary is a scalar
                        if value.numel() != 1:
                            raise ValueError(
                                f"Boundary array for 1D grid at dim {dim}, side {side} "
                                f"should be a scalar, got shape {value.shape}"
                            )
                    elif value.ndim == self.ndim-1 and value.shape != expected_shape:
                        raise ValueError(
                            f"Boundary array for dim {dim}, side {side} has shape "
                            f"{value.shape}, expected {expected_shape}"
                        )

    @property
    def bc_values(
        self,
    ) -> Sequence[Tuple[Optional[BCValues], Optional[BCValues]]]:
        """Returns boundary values as tensors for each boundary.

        For callable boundary conditions, this will raise an error asking the user
        to use FunctionBoundaryConditions instead.
        For float boundary conditions, returns tensors with the constant value.
        For tensor boundary conditions, returns them as-is.
        For None, returns None.
        """
        if self.has_callable:
            raise ValueError(
                "Callable boundary conditions detected. Please use "
                "FunctionBoundaryConditions class for callable boundary conditions."
            )

        # Process non-callable values
        result = []
        for dim in range(self.ndim):
            dim_values = []
            for side in range(2):
                value = self._bc_values[dim][side]
                if value is None:
                    dim_values.append(None)
                elif isinstance(value, torch.Tensor):
                    dim_values.append(value)
                elif isinstance(value, (int, float)):
                    # Return scalar tensor for float values
                    dim_values.append(torch.tensor(float(value)))
                else:
                    raise ValueError(f"Unsupported boundary value type: {type(value)}")
            result.append(tuple(dim_values))
        return tuple(result)

    def __repr__(self) -> str:
        try:
            lines = [f"VariableBoundaryConditions({self.ndim}D):"]

            for dim in range(self.ndim):
                lower_type, upper_type = self.types[dim]
                lower_val, upper_val = self._bc_values[dim]

                # Format values based on type
                def format_value(val):
                    if val is None:
                        return "None"
                    elif isinstance(val, torch.Tensor):
                        return f"Tensor{tuple(val.shape)}"
                    elif callable(val):
                        return f"Callable({val.__name__ if hasattr(val, '__name__') else 'lambda'})"
                    else:
                        return str(val)

                lower_val_str = format_value(lower_val)
                upper_val_str = format_value(upper_val)

                lines.append(
                    f"  dim {dim}: [{lower_type}({lower_val_str}), {upper_type}({upper_val_str})]"
                )

            return "\n".join(lines)
        except Exception as e:
            return f"VariableBoundaryConditions not initialized: {e}"

    def clone(
        self,
        types: Optional[Sequence[Tuple[str, str]]] = None,
        values: Optional[
            Sequence[
                Tuple[
                    BCValues,
                    BCValues,
                ]
            ]
        ] = None,
    ) -> BoundaryConditions:
        """Creates a copy with optionally modified parameters."""
        new_types = types if types is not None else self.types
        new_values = values if values is not None else self._bc_values
        return DiscreteBoundaryConditions(new_types, new_values)

    def _boundary_slices(
        self, offset: Tuple[float, ...]
    ) -> Tuple[Tuple[Optional[slice], Optional[slice]], ...]:
        """Returns slices for boundary values after considering trimming effects.

        When a GridVariable with certain offsets gets trimmed, the boundary coordinates
        need to be sliced accordingly to match the trimmed interior data.
        Currently, this only works for 2D grids (spatially the variable lives on a 2D grid, i.e., good for 2D+time+channel variables).

        Args:
            offset: The offset of the GridVariable
            grid: The grid associated with the GridVariable

        Returns:
            A tuple of (lower_slice, upper_slice) for each dimension, where each slice
            indicates how to index the boundary values for that dimension and side.
            (None, None) means no slicing needed (use full boundary array).
        """
        if self.ndim > 2:
            raise NotImplementedError(
                "Multi-dimensional boundary slicing not implemented"
            )
        if len(offset) != self.ndim:
            raise ValueError(
                f"Offset length {len(offset)} doesn't match number of sets of boundary edges {self.ndim}"
            )

        # Initialize with default "no slicing" tuples
        slices: List[Tuple[Optional[slice], Optional[slice]]] = [
            (None, None),
            (None, None),
        ]

        for dim in range(self.ndim):
            other_dim = dim ^ 1  # flip the bits to get the other dimension index
            trimmed_lower = math.isclose(offset[dim], 0.0)
            trimmed_upper = math.isclose(offset[dim], 1.0)

            assert not (
                trimmed_lower and trimmed_upper
            ), "MAC grids cannot ahve both lower and upper trimmed for bc."
            if trimmed_lower:
                slices[other_dim] = (slice(1, None), slice(1, None))
            elif trimmed_upper:
                slices[other_dim] = (slice(None, -1), slice(None, -1))
            # else: keep the default (None, None)

        return tuple(slices)

    def _boundary_mesh(
        self,
        dim: int,
        grid: Grid,
        offset: Tuple[float, ...],
    ) -> Tuple[Tuple[torch.Tensor, ...], Tuple[torch.Tensor, ...]]:
        """Get coordinate arrays for boundary points along dimension dim."""
        # Use the Grid's boundary_mesh method and return coordinates for lower boundary
        # (both lower and upper have same coordinate structure for the boundary points)
        return grid.boundary_mesh(dim, offset)

    def pad_and_impose_bc(
        self,
        u: GridVariable,
        offset_to_pad_to: Optional[Tuple[float, ...]] = None,
        mode: Optional[str] = "",
    ) -> GridVariable:
        """Pad and impose variable boundary conditions."""
        assert u.bc is None, "u must be trimmed before padding and imposing bc."
        if offset_to_pad_to is None:
            offset_to_pad_to = u.offset

        bc_values = self.bc_values
        boundary_slices = self._boundary_slices(offset_to_pad_to)
        x_boundary_slice = boundary_slices[-2]

        if not all(s is None for s in x_boundary_slice):
            # Apply slicing to boundary values
            new_bc_values = list(list(v) for v in bc_values)
            for i in range(2):
                if bc_values[-2][i] is not None:
                    if bc_values[-2][i].ndim > 0:
                        new_bc_values[-2][i] = bc_values[-2][i][x_boundary_slice[i]]
                    else:
                        new_bc_values[-2][i] = bc_values[-2][i]
            bc_values = new_bc_values

        for dim in range(-u.grid.ndim, 0):
            _ = self._is_aligned(u, dim)
            if self.types[dim][0] != BCType.PERIODIC:
                # the values passed to grids.pad should consider the offset of the variable
                # if the offset is 1, the the trimmed variable will have the upper edge of that dimension trimmed, one only needs n-1 entries.
                if mode:
                    u = grids.pad(u, (1, 1), dim, self, mode=mode, values=bc_values)
                elif self.types[dim][0] == BCType.DIRICHLET and not mode:
                    if math.isclose(offset_to_pad_to[dim], 1.0):
                        u = grids.pad(u, 1, dim, self, values=bc_values)
                    elif math.isclose(offset_to_pad_to[dim], 0.0):
                        u = grids.pad(u, -1, dim, self, values=bc_values)
                elif self.types[dim][0] == BCType.NEUMANN and not mode:
                    if not math.isclose(offset_to_pad_to[dim], 0.5):
                        raise ValueError("Neumann bc is not defined on edges.")
                else:
                    raise NotImplementedError(
                        f"Padding for {self.types[dim][0]} boundary conditions is not implemented."
                    )

        return GridVariable(u.data, u.offset, u.grid, self)


@dataclasses.dataclass(init=False, frozen=True, repr=False)
class FunctionBoundaryConditions(DiscreteBoundaryConditions):
    """Boundary conditions defined by callable functions.

    This class handles boundary conditions that are defined as functions of
    spatial coordinates (and optionally time). The functions are automatically
    evaluated on the boundary mesh during initialization.

    Attributes:
        types: boundary condition types for each dimension
        _bc_values: evaluated boundary values (tensors/floats after evaluation)
        ndim: number of spatial dimensions

    Example usage:
        # Function-based boundary conditions with individual functions
        def left_bc(x, y):
            return torch.sin(y)

        def right_bc(x, y):
            return torch.cos(y)

        grid = Grid((10, 20))
        bc = FunctionBoundaryConditions(
            types=((BCType.DIRICHLET, BCType.DIRICHLET),
                   (BCType.NEUMANN, BCType.DIRICHLET)),
            values=((left_bc, right_bc),    # left/right boundaries
                    (None, lambda x, y: x**2))  # bottom/top boundaries
            grid=grid,
            offset=(0.5, 0.5)
        )

        # Or with a single function applied to all boundaries
        def global_bc(x, y):
            return x + y

        bc = FunctionBoundaryConditions(
            types=((BCType.DIRICHLET, BCType.DIRICHLET),
                   (BCType.DIRICHLET, BCType.DIRICHLET)),
            values=global_bc,  # Single function applied everywhere
            grid=grid,
            offset=(0.5, 0.5)
        )
    """

    _raw_bc_values: Tuple[
        Tuple[
            Union[
                Callable[..., torch.Tensor],
                Union[Callable[..., torch.Tensor], BCValues, float],
            ],
            BCValues,
            float,
        ],
        ...,
    ]

    def __init__(
        self,
        types: Sequence[Tuple[str, str]],
        values: Union[
            Callable[..., torch.Tensor],  # Single function for all boundaries
            Sequence[
                Tuple[
                    Union[Callable[..., torch.Tensor], BCValues, float],
                    Union[Callable[..., torch.Tensor], BCValues, float],
                ]
            ],
        ],
        grid: Grid,
        offset: Optional[Tuple[float, ...]] = None,
        time: Optional[torch.Tensor] = None,
    ):
        """Initialize function-based boundary conditions.

        Args:
            types: boundary condition types for each dimension
            values: boundary values that can be:
                - Single Callable: function to apply to all boundaries
                - Sequence of tuples: individual values per boundary that can be:
                    - Callable: function to evaluate on boundary mesh
                    - torch.Tensor: precomputed values along boundary
                    - float/int: constant value
                    - None: homogeneous boundary condition
            grid: Grid to evaluate boundary conditions on
            offset: Grid offset for boundary coordinate calculation
            time: Optional time parameter for time-dependent boundary conditions
        """
        types = tuple(types)

        # Handle single callable function case
        if callable(values):
            # Apply the same function to all boundaries
            ndim = len(types)
            values = tuple((values, values) for _ in range(ndim))
        else:
            values = tuple(values)

        # Set basic attributes first
        object.__setattr__(self, "_types", types)
        object.__setattr__(self, "ndim", len(types))
        object.__setattr__(self, "_raw_bc_values", values)

        if offset is None:
            offset = grid.cell_center

        # Evaluate callable boundary conditions
        evaluated_values = []

        for dim in range(len(types)):
            dim_values = []

            # Get boundary coordinates for this dimension if needed
            boundary_coords = None

            for side in range(2):
                value = values[dim][side]

                if value is None:
                    dim_values.append(None)
                elif isinstance(value, torch.Tensor):
                    dim_values.append(value)
                elif isinstance(value, (int, float)):
                    dim_values.append(torch.tensor(float(value)))
                elif isinstance(value, Callable):
                    # Get boundary coordinates if not already computed
                    if boundary_coords is None:
                        lower_coords, upper_coords = grid.boundary_mesh(dim, offset)
                        boundary_coords = (lower_coords, upper_coords)

                    # Evaluate callable on appropriate boundary
                    boundary_points = boundary_coords[side]
                    if time is not None:
                        evaluated_value = value(*boundary_points, t=time)
                    else:
                        evaluated_value = value(*boundary_points)
                    dim_values.append(evaluated_value)
                else:
                    raise ValueError(f"Unsupported boundary value type: {type(value)}")

            evaluated_values.append(tuple(dim_values))

        # Set the evaluated values
        object.__setattr__(self, "_bc_values", tuple(evaluated_values))

        # Validate the evaluated arrays
        self._validate_boundary_arrays_with_grid(grid)

    @property
    def has_callable(self) -> bool:
        """Always returns False since all callables are evaluated during init."""
        return False

    @property
    def bc_values(
        self,
    ) -> Sequence[Tuple[Optional[BCValues], Optional[BCValues]]]:
        """Returns boundary values as tensors for each boundary.

        Since all callable functions are evaluated during initialization,
        this property will never encounter callable values and always returns
        the evaluated tensor/float values.
        """
        # Process all values (no callables should exist at this point)
        result = []
        for dim in range(self.ndim):
            dim_values = []
            for side in range(2):
                value = self._bc_values[dim][side]
                if value is None:
                    dim_values.append(None)
                elif isinstance(value, torch.Tensor):
                    dim_values.append(value)
                elif isinstance(value, (int, float)):
                    # Return scalar tensor for float values
                    dim_values.append(torch.tensor(float(value)))
                else:
                    raise ValueError(
                        f"Unexpected boundary value type after evaluation: {type(value)}"
                    )
            result.append(tuple(dim_values))
        return tuple(result)


def dirichlet_boundary_conditions_nonhomogeneous(
    ndim: int,
    bc_values: Sequence[Tuple[BCValues, BCValues]],
) -> DiscreteBoundaryConditions:
    """Create variable Dirichlet boundary conditions."""
    types = ((BCType.DIRICHLET, BCType.DIRICHLET),) * ndim
    return DiscreteBoundaryConditions(types, bc_values)


def neumann_boundary_conditions_nonhomogeneous(
    ndim: int,
    bc_values: Sequence[Tuple[BCValues, BCValues],],
) -> DiscreteBoundaryConditions:
    """Create variable Neumann boundary conditions."""
    types = ((BCType.NEUMANN, BCType.NEUMANN),) * ndim
    return DiscreteBoundaryConditions(types, bc_values)

def function_boundary_conditions_nonhomogeneous(
    ndim: int,
    bc_function: Callable[..., torch.Tensor],
    bc_type: str,
    grid: Grid,
    offset: Optional[Tuple[float, ...]] = None,
    time: Optional[torch.Tensor] = None,
) -> FunctionBoundaryConditions:
    """Create function boundary conditions with the same function applied to all boundaries.
    """
    types = ((bc_type, bc_type),) * ndim
    return FunctionBoundaryConditions(types, bc_function, grid, offset, time)

def _count_bc_components(bc: BoundaryConditions) -> int:
    """Counts the number of components in the boundary conditions.

    Returns:
        The number of components in the boundary conditions.
    """
    count = 0
    ndim = len(bc.types)
    for dim in range(ndim):  # ndim
        if len(bc.types[dim]) != 2:
            raise ValueError(
                f"Boundary conditions for axis {dim} must have two values got {len(bc.types[dim])}."
            )
        count += len(bc.types[dim])
    return count


def consistent_boundary_conditions_grid(
    grid, *arrays: GridVariable
) -> Tuple[GridVariable, ...]:
    """Returns the updated boundary condition if the number of components is inconsistent
    with the grid
    """
    bc_counts = []
    for array in arrays:
        bc_counts.append(_count_bc_components(array.bc))
    bc_count = bc_counts[0]
    if any(bc_counts[i] != bc_count for i in range(1, len(bc_counts))):
        raise Exception("Boundary condition counts are inconsistent")
    if any(bc_counts[i] != 2 * grid.ndim for i in range(len(bc_counts))):
        raise ValueError(
            f"Boundary condition counts {bc_counts} are inconsistent with grid dimensions {grid.ndim}"
        )
    return arrays


def consistent_boundary_conditions_gridvariable(
    *arrays: GridVariable,
) -> Tuple[str, ...]:
    """Returns whether BCs are periodic.

    Mixed periodic/nonperiodic boundaries along the same boundary do not make
    sense. The function checks that the boundary is either periodic or not and
    throws an error if its mixed.

    Args:
      *arrays: a list of gridvariables.

    Returns:
      a list of types of boundaries corresponding to each axis if
      they are consistent.
    """
    bc_types = []
    for dim in range(arrays[0].grid.ndim):
        bcs = {is_periodic_boundary_conditions(array, dim) for array in arrays}
        if len(bcs) != 1:
            raise Exception(f"arrays do not have consistent bc: {arrays}")
        elif bcs.pop():
            bc_types.append("periodic")
        else:
            bc_types.append("nonperiodic")
    return tuple(bc_types)


def get_pressure_bc_from_velocity_bc(
    bcs: Tuple[BoundaryConditions, ...],
) -> HomogeneousBoundaryConditions:
    """Returns pressure boundary conditions for the specified velocity BCs.
    if the velocity BC is periodic, the pressure BC is periodic.
    if the velocity BC is nonperiodic, the pressure BC is zero flux (homogeneous Neumann).
    """
    # assumes that if the boundary is not periodic, pressure BC is zero flux.
    pressure_bc_types = []

    for velocity_bc in bcs:
        if is_bc_periodic_boundary_conditions(velocity_bc, 0):
            pressure_bc_types.append((BCType.PERIODIC, BCType.PERIODIC))
        else:
            pressure_bc_types.append((BCType.NEUMANN, BCType.NEUMANN))

    return HomogeneousBoundaryConditions(pressure_bc_types)


def get_pressure_bc_from_velocity(
    v: GridVariableVector,
) -> HomogeneousBoundaryConditions:
    """Returns pressure boundary conditions for the specified velocity."""
    # assumes that if the boundary is not periodic, pressure BC is zero flux.
    velocity_bc_types = consistent_boundary_conditions_gridvariable(*v)
    pressure_bc_types = []
    for velocity_bc_type in velocity_bc_types:
        if velocity_bc_type == "periodic":
            pressure_bc_types.append((BCType.PERIODIC, BCType.PERIODIC))
        else:
            pressure_bc_types.append((BCType.NEUMANN, BCType.NEUMANN))
    return HomogeneousBoundaryConditions(pressure_bc_types)


def has_all_periodic_boundary_conditions(*arrays: GridVariable) -> bool:
    """Returns True if arrays have periodic BC in every dimension, else False."""
    for array in arrays:
        for dim in range(array.grid.ndim):
            if not is_periodic_boundary_conditions(array, dim):
                return False
    return True


def get_advection_flux_bc_from_velocity_and_scalar_bc(
    u_bc: BoundaryConditions, c_bc: BoundaryConditions, flux_direction: int
) -> ConstantBoundaryConditions:
    """Returns advection flux boundary conditions for the specified velocity.

    Infers advection flux boundary condition in flux direction
    from scalar c and velocity u in direction flux_direction.
    The flux boundary condition should be used only to compute divergence.
    If the boundaries are periodic, flux is periodic.
    In nonperiodic case, flux boundary parallel to flux direction is
    homogeneous dirichlet.
    In nonperiodic case if flux direction is normal to the wall, the
    function supports multiple cases:
      1) Nonporous boundary, corresponding to homogeneous flux bc.
      2) Porous boundary with constant flux, corresponding to
        both the velocity and scalar with Homogeneous Neumann bc.
      3) Non-homogeneous Dirichlet velocity with Dirichlet scalar bc.

    Args:
      u_bc: bc of the velocity component in flux_direction.
      c_bc: bc of the scalar to advect.
      flux_direction: direction of velocity.

    Returns:
      BoundaryCondition instance for advection flux of c in flux_direction.

    Example:
    >>> u_bc = ConstantBoundaryConditions(((BCType.DIRICHLET, BCType.DIRICHLET),),  ((1.0, 2.0),))

    >>> c_bc = ConstantBoundaryConditions(((BCType.DIRICHLET, BCType.DIRICHLET),), ((0.5, 1.5),))

    >>> flux_bc = get_advection_flux_bc_from_velocity_and_scalar_bc(u_bc, c_bc,0)
    # flux_bc will have values (0.5, 3.0) = (1.0*0.5, 2.0*1.5)
    """
    flux_bc_types = []
    flux_bc_values = []

    # Handle both homogeneous and non-homogeneous boundary conditions
    # cannot handle mixed boundary conditions yet.
    if isinstance(u_bc, HomogeneousBoundaryConditions):
        u_values = tuple((0.0, 0.0) for _ in range(u_bc.ndim))
    elif isinstance(u_bc, ConstantBoundaryConditions):
        u_values = u_bc.bc_values
    else:
        raise NotImplementedError(
            f"Flux boundary condition is not implemented for velocity with {type(u_bc)}"
        )

    if isinstance(c_bc, HomogeneousBoundaryConditions):
        c_values = tuple((0.0, 0.0) for _ in range(c_bc.ndim))
    elif isinstance(c_bc, ConstantBoundaryConditions):
        c_values = c_bc.bc_values
    else:
        raise NotImplementedError(
            f"Flux boundary condition is not implemented for scalar with {type(c_bc)}"
        )

    for dim in range(c_bc.ndim):
        if u_bc.types[dim][0] == BCType.PERIODIC:
            flux_bc_types.append((BCType.PERIODIC, BCType.PERIODIC))
            flux_bc_values.append((None, None))
        elif flux_direction != dim:
            # Flux boundary condition parallel to flux direction
            # Set to homogeneous Dirichlet as it doesn't affect divergence computation
            flux_bc_types.append((BCType.DIRICHLET, BCType.DIRICHLET))
            flux_bc_values.append((0.0, 0.0))
        else:
            # Flux direction is normal to the boundary
            flux_bc_types_ax = []
            flux_bc_values_ax = []

            for i in range(2):  # lower and upper boundary
                u_type = u_bc.types[dim][i]
                c_type = c_bc.types[dim][i]
                u_val = u_values[dim][i] if u_values[dim][i] is not None else 0.0
                c_val = c_values[dim][i] if c_values[dim][i] is not None else 0.0

                # Case 1: Dirichlet velocity with Dirichlet scalar
                if u_type == BCType.DIRICHLET and c_type == BCType.DIRICHLET:
                    # Flux = u * c at the boundary
                    flux_val = u_val * c_val
                    flux_bc_types_ax.append(BCType.DIRICHLET)
                    flux_bc_values_ax.append(flux_val)

                # Case 2: Neumann velocity with Neumann scalar (zero flux condition)
                elif u_type == BCType.NEUMANN and c_type == BCType.NEUMANN:
                    # For zero flux: du/dn = 0 and dc/dn = 0 implies d(uc)/dn = 0
                    if not math.isclose(u_val, 0.0) or not math.isclose(c_val, 0.0):
                        raise NotImplementedError(
                            "Non-homogeneous Neumann boundary conditions for flux "
                            "are not yet implemented"
                        )
                    flux_bc_types_ax.append(BCType.NEUMANN)
                    flux_bc_values_ax.append(0.0)

                # Case 3: Mixed boundary conditions
                elif u_type == BCType.DIRICHLET and c_type == BCType.NEUMANN:
                    # If u is specified and dc/dn is specified, we can compute flux
                    # flux = u * c, but c is not directly specified
                    # This requires more complex handling - for now, raise error
                    raise NotImplementedError(
                        "Mixed Dirichlet velocity and Neumann scalar boundary "
                        "conditions are not yet implemented"
                    )

                elif u_type == BCType.NEUMANN and c_type == BCType.DIRICHLET:
                    # If du/dn is specified and c is specified
                    # This also requires more complex handling
                    raise NotImplementedError(
                        "Mixed Neumann velocity and Dirichlet scalar boundary "
                        "conditions are not yet implemented"
                    )

                else:
                    raise NotImplementedError(
                        f"Flux boundary condition is not implemented for "
                        f"u_bc={u_type} with value={u_val}, "
                        f"c_bc={c_type} with value={c_val}"
                    )

            flux_bc_types.append(tuple(flux_bc_types_ax))
            flux_bc_values.append(tuple(flux_bc_values_ax))

    return ConstantBoundaryConditions(flux_bc_types, flux_bc_values)


def get_advection_flux_bc_from_velocity_and_scalar(
    u: GridVariable, c: GridVariable, flux_direction: int
) -> ConstantBoundaryConditions:
    return get_advection_flux_bc_from_velocity_and_scalar_bc(u.bc, c.bc, flux_direction)
