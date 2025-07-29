from __future__ import annotations  # noqa

from typing import TYPE_CHECKING, Optional
from warnings import warn

import numpy as np
from contourpy import contour_generator
from numpy.typing import ArrayLike
from shapely import distance
from shapely.geometry import LineString, Point

from ..dataset_wrapper import DatasetWrapper
from ..units import ureg as units
from .utils import eq_units

if TYPE_CHECKING:
    import matplotlib.pyplot as plt


@units.wraps(
    units.meter,
    [units.m, units.m, units.weber / units.rad] * 2 + [units.weber / units.rad],
    strict=False,
)
def _flux_surface_contour(
    R: ArrayLike,
    Z: ArrayLike,
    psi_RZ: ArrayLike,
    R_axis: float,
    Z_axis: float,
    psi: float,
    psi_lcfs: float = None,
) -> np.ndarray:
    r"""
    Given linearly-spaced RZ coordinates and :math:`\psi` at these positions, returns
    the R and Z coordinates of a contour at given psi. Describes the path of a single
    magnetic flux surface within a tokamak. Aims to return the closest closed contour to
    the position ``(R_axis, Z_axis)``.

    Parameters
    ----------
    R: ArrayLike
        Linearly spaced and monotonically increasing 1D grid of major radius
        coordinates, i.e. the radial distance from the central column of a tokamak.
    Z: ArrayLike
        Linearly spaced and monotonically increasing 1D grid of z-coordinates describing
        the distance from the midplane of a tokamak.
    psi_RZ: ArrayLike
        2D grid of :math:`\psi`, the poloidal magnetic flux function, over the range
        (R,Z).
    R_axis: float
        R position of the magnetic axis.
    Z_axis: float
        Z position of the magnetic axis.
    psi: float
        The choice of :math:`\psi` on which to fit a contour.

    Returns
    -------
    np.ndarray
        2D array containing R and Z coordinates of the flux surface contour. Indexing
        with [0,:] gives a 1D array of R coordinates, while [1,:] gives a 1D array of
        Z coordinates. The endpoints are repeated, so [:,0] == [:,-1].

    Raises
    ------
    ValueError
        If the shapes of ``R``, ``Z``, and ``psi_RZ`` don't match.
    RuntimeError
        If no flux surface contours could be found.

    Warnings
    --------
    For performance reasons, this function does not check that ``R`` or ``Z`` are
    linearly spaced or monotonically increasing. If this condition is not upheld, the
    results are undefined.
    """

    # Check some basic conditions on R, Z, psi_RZ
    R = np.asarray(R, dtype=float)
    Z = np.asarray(Z, dtype=float)
    psi_RZ = np.asarray(psi_RZ, dtype=float)
    if len(R.shape) != 1:
        raise ValueError("The grid R should be 1D.")
    if len(Z.shape) != 1:
        raise ValueError("The grid Z should be 1D.")
    if not np.array_equal(psi_RZ.shape, (len(R), len(Z))):
        raise ValueError(
            f"The grid psi_RZ has shape {psi_RZ.shape}. "
            f"It should have shape {(len(R), len(Z))}."
        )
    # Get contours, raising error if none are found: added by Juan 13/02/2025
    if psi < np.min(psi_RZ):
        raise ValueError(f"psi={psi} is out of range (min): [{np.min(psi_RZ)}])")
    if psi > np.max(psi_RZ):
        raise ValueError(f"psi={psi} is out of range (max): [{np.max(psi_RZ)}])")

    # Get contours, raising error if none are found
    cont_gen = contour_generator(x=Z, y=R, z=psi_RZ)
    contours = cont_gen.lines(psi)

    if not contours:
        raise RuntimeError(f"Could not find flux surface contours for psi={psi}")

    # Find the contour that is, on average, closest to the magnetic axis, as this
    # procedure may find additional open contours outside the last closed flux surface.
    if len(contours) > 1:
        RZ_axis = np.array([Z_axis, R_axis])
        if psi == psi_lcfs:
            new_contours = []
            for c, contour_line in enumerate(contours):
                new_contour = []

                contour_ls = LineString(contour_line[:, ::-1])
                origin = Point(R_axis, Z_axis)
                for i, point in enumerate(contour_line):
                    direction = (point[1] - R_axis, point[0] - Z_axis)
                    line = LineString(
                        [
                            origin,
                            Point(
                                origin.x + 2 * direction[0], origin.y + 2 * direction[1]
                            ),
                        ]
                    )
                    intersection = contour_ls.intersection(line)
                    if intersection.geom_type == "Point":
                        # Ensure intersection is in original contour
                        if np.isclose(point[1], intersection.x) and np.isclose(
                            point[0], intersection.y
                        ):
                            new_contour.append([intersection.y, intersection.x])
                    elif intersection.geom_type == "MultiPoint":
                        min_distance_idx = np.argmin(
                            [distance(inter, origin) for inter in intersection.geoms]
                        )
                        min_distance_R = intersection.geoms[min_distance_idx].x
                        min_distance_Z = intersection.geoms[min_distance_idx].y
                        # Ensure intersection is in original contour
                        if np.isclose(point[1], min_distance_R) and np.isclose(
                            point[0], min_distance_Z
                        ):
                            new_contour.append([min_distance_Z, min_distance_R])
                new_contour = np.array(new_contour)
                new_contours.append(new_contour)
            contours = new_contours

        mean_dist = [np.mean(np.linalg.norm(c - RZ_axis, axis=1)) for c in contours]
        contour = contours[np.argmin(mean_dist)]
    else:
        contour = contours[0]

    # The contour will be arranged as [[Z0, R0], [Z1, R1], ..., [ZN, RN], [Z0, R0]]
    # R0 and Z0 can be any points on the contour. We instead need the following:
    # - Grids should be arranged [[R0, R1, ..., RN, R0], [Z0, Z1, ..., ZN, Z0]]
    # - R0 and Z0 should be at the outside midplane (OMP).
    # - The contour should be ordered in the clockwise direction, following COCOS 11

    # Discard the endpoint, swap the order of R and Z, and transpose
    # This gives [[R0, R1, ..., RN], [Z0, Z1, ..., ZN]]
    contour = contour[:-1, ::-1].T

    # Get the index of the OMP and move this to the start of the array
    omp_idx = np.argmax(contour[0])

    # Adjust the contour arrays so that we begin at the OMP
    contour = np.roll(contour, -omp_idx, axis=1)

    # Reintroduce the endpoints
    contour = np.column_stack((contour, contour[:, 0]))

    # Ensure theta increases in a clockwise direction
    if contour[1, 1] > contour[1, 0]:
        contour = contour[:, ::-1]

    return contour


class FluxSurface(DatasetWrapper):
    r"""
    Information about a single flux surface of a tokamak plasma equilibrium. Users are
    not expected to initialise ``FluxSurface`` objects directly, but instead should
    generate them from ``Equilibrium`` objects. ``FluxSurface`` is used as an
    intermediate object when generating ``LocalGeometry`` objects from global plasma
    equilibria. For more information, see the 'Notes' section for ``Equilibrium``.

    Parameters
    ----------

    R: ArrayLike, units [meter]
        1D grid of major radius coordinates describing the path of the flux surface.
        The endpoints should be repead.
    Z: ArrayLike, units [meter]
        1D grid of tokamak Z-coordinates describing the path of the flux surface.
        This is usually the height above the plasma midplane, but Z=0 may be set at any
        reference point. Should have same length as ``R``, and the endpoints should be
        repeated.
    B_poloidal: ArrayLike, units [tesla]
        1D grid of the magnitude of the poloidal magnetic field following the path
        described by R and Z. Should have the same length as ``R``.
    R_major: float, units [meter]
        The major radius position of the center of each flux surface. This should be
        given by the mean of the maximum and minimum major radii of the flux surface.
    r_minor: float, units [meter]
        The minor radius of the flux surface. This should be half of the difference
        between the maximum and minimum major radii of the flux surface.
    Z_mid: float, units [meter]
        The z-midpoint of the flux surface. This should be the mean of the maximum and
        minimum z-positions of the flux surface.
    F: float, units [meter * tesla]
        The poloidal current function.
    FF_prime: float, units [meter**2 * tesla**2 / weber]
        1D grid defining the poloidal current function ``f`` multiplied by its
        derivative with respect to ``psi``. Should have the same length as ``psi``.
    p: float, units [pascal]
        Plasma pressure.
    q: float, units [dimensionless]
        The safety factor.
    magnetic_shear: float, units [dimensionless]
        Defined as :math:`\frac{r}{q}\frac{dq}{dr}`, where :math:`r` is the minor radius
        and :math:`q` is the safety factor.
    shafranov_shift: float, units [dimensionless]
        The derivative of `R_major` with respect to `r_minor`
    midplane_shift: float, units [dimensionless]
        The derivative of `Z_mid` with respect to `r_minor`
    pressure_gradient: float, units [pascal / meter]
        The derivative of pressure with respect to `r_minor`.
    psi_gradient: float, units [weber / meter]
        The derivative of the poloidal magnetic flux function :math:`\psi` with respect
        to `r_minor`.
    a_minor: float, units [meter]
        The minor radius of the last closed flux surface (LCFS). Though not necessarily
        applicable to this flux surface, a_minor is often used as a reference length in
        gyrokinetic simulations.

    Attributes
    ----------

    data: xarray.Dataset
        The internal representation of the ``FluxSurface`` object. The function
        ``__getitem__`` redirects indexing lookups here, but the Dataset itself may be
        accessed directly by the user if they wish to perform more complex actions.
    rho: float, units [dimensionless]
    R_major: float, units [meter]
    r_minor: float, units [meter]
    Z_mid: float, units [meter]
    F: float, units [meter * tesla]
    FF_prime: float, units [meter**2 * tesla**2 / weber]
    p: float, units [pascal]
    q: float, units [dimensionless]
    magnetic_shear: float, units [dimensionless]
    shafranov_shift: float, units [dimensionless]
    midplane_shift: float, units [dimensionless]
    pressure_gradient: float, units [pascal / meter]
    psi_gradient: float, units [weber / meter]
    a_minor: float, units [meter]

    See Also
    --------

    Equilibrium: Object representing a global equilibrium.
    """

    # This dict defines the units for each argument to __init__.
    # The values are passed to the units.wraps decorator.
    _init_units = {
        "self": None,
        "R": eq_units["len"],
        "Z": eq_units["len"],
        "B_poloidal": eq_units["B"],
        "R_major": eq_units["len"],
        "r_minor": eq_units["len"],
        "Z_mid": eq_units["len"],
        "F": eq_units["F"],
        "FF_prime": eq_units["FF_prime"],
        "p": eq_units["p"],
        "q": eq_units["q"],
        "magnetic_shear": units.dimensionless,
        "shafranov_shift": units.dimensionless,
        "midplane_shift": units.dimensionless,
        "pressure_gradient": eq_units["p"] / eq_units["len"],
        "psi_gradient": eq_units["psi"] / eq_units["len"],
        "a_minor": eq_units["len"],
    }

    @units.wraps(None, [*_init_units.values()], strict=False)
    def __init__(
        self,
        R: np.ndarray,
        Z: np.ndarray,
        B_poloidal: np.ndarray,
        R_major: float,
        r_minor: float,
        Z_mid: float,
        F: float,
        FF_prime: float,
        p: float,
        q: float,
        magnetic_shear: float,
        shafranov_shift: float,
        midplane_shift: float,
        pressure_gradient: float,
        psi_gradient: float,
        a_minor: float,
    ):
        # Check floats
        R_major = float(R_major) * eq_units["len"]
        r_minor = float(r_minor) * eq_units["len"]
        Z_mid = float(Z_mid) * eq_units["len"]
        F = float(F) * eq_units["F"]
        FF_prime = float(FF_prime) * eq_units["FF_prime"]
        p = float(p) * eq_units["p"]
        q = float(q) * eq_units["q"]
        magnetic_shear = float(magnetic_shear) * units.dimensionless
        shafranov_shift = float(shafranov_shift) * units.dimensionless
        midplane_shift = float(shafranov_shift) * units.dimensionless
        pressure_gradient = float(pressure_gradient) * eq_units["p"] / eq_units["len"]
        psi_gradient = float(psi_gradient) * eq_units["psi"] / eq_units["len"]
        a_minor = float(a_minor) * eq_units["len"]

        # Check the grids R, Z, b_radial, b_vertical, and b_toroidal
        R = np.asarray(R, dtype=float) * eq_units["len"]
        Z = np.asarray(Z, dtype=float) * eq_units["len"]
        B_poloidal = np.asarray(B_poloidal, dtype=float) * eq_units["B"]
        # Check that all grids have the same shape and have matching endpoints
        RZ_grids = {
            "R": R,
            "Z": Z,
            "B_poloidal": B_poloidal,
        }
        for name, grid in RZ_grids.items():
            if len(grid.shape) != 1:
                raise ValueError(f"The grid {name} must be 1D.")
            if not np.array_equal(grid.shape, (len(R),)):
                raise ValueError(f"The grid {name} should have length {len(R)}.")
            if not np.isclose(grid[0], grid[-1]):
                raise ValueError(f"The grid {name} must have matching endpoints.")

        R_major_surface = (max(R) + min(R)) / 2

        if not np.isclose(R_major_surface, R_major, atol=1e-4):
            warn(
                f"R_major from flux surface differs from R_major in Equilibrium by {R_major_surface-R_major},"
                "likely due to interpolation defaulting to R_major_surface"
            )
            R_major = R_major_surface

        r_minor_surface = (max(R) - min(R)) / 2
        if not np.isclose(r_minor_surface, r_minor, atol=1e-4):
            warn(
                f"r_minor from flux surface differs from r_minor in Equilibrium by {r_minor_surface-r_minor},"
                "likely due to interpolation defaulting to r_minor_surface"
            )
            r_minor = r_minor_surface

        # Determine theta grid from R and Z
        # theta should increase clockwise, so Z is flipped
        theta = np.arctan2(Z_mid - Z, R - R_major)

        # Assemble grids into xarray Dataset
        def make_var(val, desc):
            return ("theta_dim", val, {"units": str(val.units), "long_name": desc})

        coords = {
            "theta": make_var(theta, "Poloidal Angle"),
        }

        data_vars = {
            "R": make_var(R, "Radial Position"),
            "Z": make_var(Z, "Vertical Position"),
            "B_poloidal": make_var(B_poloidal, "Poloidal Magnetic Flux Density"),
        }

        attrs = {
            "R_major": R_major,
            "r_minor": r_minor,
            "Z_mid": Z_mid,
            "F": F,
            "FF_prime": FF_prime,
            "p": p,
            "q": q,
            "magnetic_shear": magnetic_shear,
            "shafranov_shift": shafranov_shift,
            "midplane_shift": midplane_shift,
            "pressure_gradient": pressure_gradient,
            "psi_gradient": psi_gradient,
            "a_minor": a_minor,
            "rho": r_minor / a_minor,
        }

        super().__init__(data_vars=data_vars, coords=coords, attrs=attrs)

    def plot(
        self,
        quantity: str,
        ax: Optional[plt.Axes] = None,
        show: bool = False,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        **kwargs,
    ) -> plt.Axes:
        r"""
        Plot a quantity defined on the :math:`\theta` grid. These include ``R``,
        ``Z``, and ``B_poloidal``.

        Parameters
        ----------
        quantity: str
            Name of the quantity to plot. Must be defined over the grid ``theta``.
        ax: Optional[plt.Axes]
            Axes object on which to plot. If not provided, a new figure is created.
        show: bool, default False
            Immediately show Figure after creation.
        x_label: Optional[str], default None
            Overwrite the default x label. Set to an empty string ``""`` to disable.
        y_label: Optional[str], default None
            Overwrite the default y label. Set to an empty string ``""`` to disable.
        **kwargs
            Additional arguments to pass to Matplotlib's ``plot`` call.

        Returns
        -------
        plt.Axes
            The Axes object created after plotting.

        Raises
        ------
        ValueError
            If ``quantity`` is not a quantity defined over the :math:`\theta` grid,
            or is not the name of a FluxSurface quantity.
        """
        import matplotlib.pyplot as plt

        if quantity not in self.data_vars:
            raise ValueError(
                f"Must be provided with a quantity defined on the theta grid."
                f"The quantity '{quantity}' is not recognised."
            )

        quantity_dims = self[quantity].dims
        if "theta_dim" not in quantity_dims or len(quantity_dims) != 1:
            raise ValueError(
                f"Must be provided with a quantity defined on the theta grid."
                f"The quantity '{quantity}' has coordinates {quantity_dims}."
            )

        if ax is None:
            _, ax = plt.subplots(1, 1)

        x_data = self["theta"]
        if x_label is None:
            x_label = f"{x_data.long_name} / ${x_data.data.units:L~}$"

        y_data = self[quantity]
        if y_label is None:
            y_label = f"{y_data.long_name} / ${y_data.data.units:L~}$"

        ax.plot(x_data.data.magnitude, y_data.data.magnitude, **kwargs)
        if x_label != "":
            ax.set_xlabel(x_label)
        if y_label != "":
            ax.set_ylabel(y_label)

        if show:
            plt.show()

        return ax

    def plot_path(
        self,
        ax: Optional[plt.Axes] = None,
        aspect: bool = False,
        show: bool = False,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        **kwargs,
    ) -> plt.Axes:
        r"""
        Plot the path of the flux surface in :math:`(R, Z)` coordinates.

        Parameters
        ----------
        ax: Optional[plt.Axes]
            Axes object on which to plot. If not provided, a new figure is created.
        aspect: bool, default False
            If True, ensures the axes have the correct aspect ratio. If the user
            supplies their own ``ax``, has no effect.
        show: bool, default False
            Immediately show Figure after creation.
        x_label: Optional[str], default None
            Overwrite the default x label. Set to an empty string ``""`` to disable.
        y_label: Optional[str], default None
            Overwrite the default y label. Set to an empty string ``""`` to disable.
        **kwargs
            Additional arguments to pass to Matplotlib's ``plot`` call.

        Returns
        -------
        plt.Axes
            The Axes object created after plotting.
        """
        import matplotlib.pyplot as plt

        x_data = self["R"]
        if x_label is None:
            x_label = f"{x_data.long_name} / ${x_data.data.units:L~}$"

        y_data = self["Z"]
        if y_label is None:
            y_label = f"{y_data.long_name} / ${y_data.data.units:L~}$"

        if ax is None:
            _, ax = plt.subplots(1, 1)
            if aspect:
                ax.set_aspect("equal")

        ax.plot(x_data.data.magnitude, y_data.data.magnitude, **kwargs)
        if x_label != "":
            ax.set_xlabel(x_label)
        if y_label != "":
            ax.set_ylabel(y_label)

        if show:
            plt.show()

        return ax
