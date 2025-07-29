from typing import Tuple

import numpy as np
from scipy.integrate import simpson
from scipy.optimize import least_squares  # type: ignore

from ..typing import ArrayLike
from ..units import PyroQuantity
from ..units import ureg as units
from .local_geometry import LocalGeometry, default_inputs


def default_mxh_inputs(n_moments: int = 4):
    # Return default args to build a LocalGeometryMXH
    # Uses a function call to avoid the user modifying these values

    base_defaults = default_inputs()
    mxh_defaults = {
        "cn": np.zeros(n_moments),
        "dcndr": np.zeros(n_moments),
        "sn": np.zeros(n_moments),
        "dsndr": np.zeros(n_moments),
        "local_geometry": "MXH",
        "n_moments": n_moments,
    }

    return {**base_defaults, **mxh_defaults}


class LocalGeometryMXH(LocalGeometry):
    r"""Local equilibrium representation defined as in: `PPCF 63 (2021) 012001
    (5pp) <https://doi.org/10.1088/1361-6587/abc63b>`_

    Miller eXtended Harmonic (MXH)

    .. math::
        \begin{align}
        R(r, \theta) &= R_{major}(r) + r \cos(\theta_R) \\
        Z(r, \theta) &= Z_0(r) + r \kappa(r) \sin(\theta) \\
        \theta_R &= \theta + c_0(r) + \sum_{n=1}^N [c_n(r) \cos(n \theta) + s_n(r) \sin(n \theta)] \\
        r &= (\max(R) - \min(R)) / 2
        \end{align}

    Data stored in a ordered dictionary

    Attributes
    ----------
    psi_n : Float
        Normalised Psi
    rho : Float
        r/a
    a_minor : Float
        Minor radius of LCFS [m]
    Rmaj : Float
        Normalised Major radius (Rmajor/a_minor)
    Z0 : Float
        Normalised vertical position of midpoint (Zmid / a_minor)
    f_psi : Float
        Torodial field function
    B0 : Float
        Toroidal field at major radius (Fpsi / Rmajor) [T]
    bunit_over_b0 : Float
        Ratio of GACODE normalising field = :math:`q/r \partial \psi/\partial r` [T] to B0
    dpsidr : Float
        :math:`\frac{\partial \psi}{\partial r}`
    q : Float
        Safety factor
    shat : Float
        Magnetic shear :math:`r/q \partial q/ \partial r`
    beta_prime : Float
        :math:`\beta = 2 \mu_0 \partial p \partial \rho 1/B0^2`

    kappa : Float
        Elongation
    s_kappa : Float
        Shear in Elongation :math:`r/\kappa \partial \kappa/\partial r`
    shift : Float
        Shafranov shift
    dZ0dr : Float
        Shear in midplane elevation
    thetaR : ArrayLike
        thetaR values at theta
    dthetaR_dtheta : ArrayLike
        Derivative of thetaR w.r.t theta at theta
    dthetaR_dr : ArrayLike
        Derivative of thetaR w.r.t r at theta
    cn : ArrayLike
        cosine moments of thetaR
    sn : ArrayLike
        sine moments of thetaR
    dcndr : ArrayLike
        Shear in cosine moments :math:`\partial c_n/\partial r`
    dsndr : ArrayLike
        Shear in sine moments :math:`\partial s_n/\partial r`

    R_eq : Array
        Equilibrium R data used for fitting
    Z_eq : Array
        Equilibrium Z data used for fitting
    b_poloidal_eq : Array
        Equilibrium B_poloidal data used for fitting
    theta_eq : Float
        theta values for equilibrium data

    R : Array
        Fitted R data
    Z : Array
        Fitted Z data
    b_poloidal : Array
        Fitted B_poloidal data
    theta : Float
        Fitted theta data

    dRdtheta : Array
        Derivative of fitted :math:`R` w.r.t :math:`\theta`
    dRdr : Array
        Derivative of fitted :math:`R` w.r.t :math:`r`
    dZdtheta : Array
        Derivative of fitted :math:`Z` w.r.t :math:`\theta`
    dZdr : Array
        Derivative of fitted :math:`Z` w.r.t :math:`r`

    d2Rdtheta2 : Array
        Second derivative of fitted :math:`R` w.r.t :math:`\theta`
    d2Rdrdtheta : Array
        Derivative of fitted :math:`R` w.r.t :math:`r` and :math:`\theta`
    d2Zdtheta2 : Array
        Second derivative of fitted :math:`Z` w.r.t :math:`\theta`
    d2Zdrdtheta : Array
        Derivative of fitted :math:`Z` w.r.t :math:`r` and :math:`\theta`

    """

    def __init__(self, *args, **kwargs):
        s_args = list(args)

        if (
            args
            and not isinstance(args[0], LocalGeometryMXH)
            and isinstance(args[0], dict)
        ):
            super().__init__(*s_args, **kwargs)

        elif len(args) == 0:
            self.default()

    def _set_shape_coefficients(
        self, R, Z, b_poloidal, verbose=False, shift=0.0, n_moments=None
    ):
        r"""
        Calculates MXH shaping coefficients from R, Z and b_poloidal

        Parameters
        ----------
        R : Array
            R for the given flux surface
        Z : Array
            Z for the given flux surface
        b_poloidal : Array
            :math:`b_\theta` for the given flux surface
        verbose : Boolean
            Controls verbosity
        shift : Float
            Initial guess for shafranov shift
        """

        if n_moments:
            self.n_moments = n_moments

        self.rho = (max(R) - min(R)) / 2

        kappa = (max(Z) - min(Z)) / (2 * self.rho)

        Zmid = (max(Z) + min(Z)) / 2

        self.Z0 = Zmid
        self.Rmaj = (max(R) + min(R)) / 2
        self.kappa = kappa

        Z_outboard = np.where(R > self.Rmaj, Z, max(Z))
        Zind_Z0 = np.argmin(abs(Z_outboard - self.Z0))
        Z = np.roll(Z.m, -Zind_Z0) * Z.units
        R = np.roll(R.m, -Zind_Z0) * R.units
        b_poloidal = np.roll(b_poloidal.m, -Zind_Z0) * b_poloidal.units

        # Need to roll eq values so theta_eq matches
        self.R_eq = R
        self.Z_eq = Z
        self.b_poloidal_eq = b_poloidal

        Zind_upper = np.argmax(Z)

        R_upper = R[Zind_upper]

        Zind_lower = np.argmin(Z)

        R_lower = R[Zind_lower]

        normalised_height = (Z - Zmid) / (kappa * self.rho)

        # Floating point error can lead to >|1.0|
        normalised_height = np.where(
            np.isclose(normalised_height, 1.0), 1.0, normalised_height
        )
        normalised_height = np.where(
            np.isclose(normalised_height, -1.0), -1.0, normalised_height
        )

        theta = np.arcsin(normalised_height)

        normalised_radius = (R - self.Rmaj) / self.rho

        normalised_radius = np.where(
            np.isclose(normalised_radius, 1.0, atol=1e-4), 1.0, normalised_radius
        )
        normalised_radius = np.where(
            np.isclose(normalised_radius, -1.0, atol=1e-4), -1.0, normalised_radius
        )

        thetaR = np.arccos(normalised_radius)

        theta = np.where((R <= R_upper) & (Z >= Zmid), np.pi - theta, theta)
        theta = np.where((R <= R_lower) & (Z <= Zmid), np.pi - theta, theta)
        theta = np.where((R > R_lower) & (Z <= Zmid), 2 * np.pi + theta, theta)
        thetaR = np.where(Z < Zmid, 2 * np.pi - thetaR, thetaR)

        # Ensure first point is close to 0 rather than 2pi
        if theta[0] > np.pi:
            theta[0] += -2 * np.pi

        if thetaR[0] > np.pi:
            thetaR[0] += -2 * np.pi

        if theta[-1] < np.pi:
            theta[-1] = 2 * np.pi - theta[-1]

        if thetaR[-1] < np.pi:
            thetaR[-1] = 2 * np.pi - thetaR[-1]

        # Add points either side to ensure we full coverage
        theta_cn = np.hstack((theta[-1] - 2 * np.pi, theta, theta[0] + 2 * np.pi))
        thetaR_cn = np.hstack((thetaR[-1] - 2 * np.pi, thetaR, thetaR[0] + 2 * np.pi))

        self.theta_eq = theta

        theta_diff = thetaR_cn - theta_cn

        theta_dimensionless = units.Quantity(theta_cn).magnitude
        theta_diff_dimensionless = units.Quantity(theta_diff).magnitude

        # Define bounds
        lower_bound = 0.0
        upper_bound = 2 * np.pi

        # Step 1: Mask values within [0, 2π]
        mask = (theta_dimensionless >= lower_bound) & (
            theta_dimensionless <= upper_bound
        )
        theta_filtered = theta_dimensionless[mask]
        theta_diff_filtered = theta_diff_dimensionless[mask]

        # Step 3: Ensure 0 and 2π are in the grid (with interpolation if necessary)
        # Check if 0 is included; if not, interpolate
        if not np.isclose(theta_filtered[0], lower_bound):
            data_0 = np.interp(
                lower_bound, theta_dimensionless, theta_diff_dimensionless
            )
            theta_filtered = np.insert(theta_filtered, 0, lower_bound)
            theta_diff_filtered = np.insert(theta_diff_filtered, 0, data_0)

        # Check if 2π is included; if not, interpolate
        if not np.isclose(theta_filtered[-1], upper_bound):
            data_2pi = np.interp(
                upper_bound, theta_dimensionless, theta_diff_dimensionless
            )
            theta_filtered = np.append(theta_filtered, upper_bound)
            theta_diff_filtered = np.append(theta_diff_filtered, data_2pi)

        ntheta = np.outer(self.n, theta_filtered)
        cn = (
            simpson(theta_diff_filtered * np.cos(ntheta), x=theta_filtered, axis=1)
            / np.pi
        )
        sn = (
            simpson(theta_diff_filtered * np.sin(ntheta), x=theta_filtered, axis=1)
            / np.pi
        )

        cn[0] *= 0.5
        sn[0] = 0.0

        self.sn = sn * units.dimensionless
        self.cn = cn * units.dimensionless

        self.theta = theta
        self.thetaR = self.get_thetaR(self.theta)
        self.dthetaR_dtheta = self.get_dthetaR_dtheta(self.theta)

        self.R, self.Z = self.get_flux_surface(self.theta)

        s_kappa_init = 0.0
        params = [shift, s_kappa_init, 0.0, *[0.0] * self.n_moments * 2]

        fits = least_squares(self.minimise_b_poloidal, params)

        # Check that least squares didn't fail
        if not fits.success:
            raise Exception(
                f"Least squares fitting in MXH::_set_shape_coefficients failed with message : {fits.message}"
            )

        if verbose:
            print(f"MXH :: Fit to Bpoloidal obtained with residual {fits.cost}")

        if fits.cost > 0.1:
            import warnings

            warnings.warn(
                f"Warning Fit to Bpoloidal in MXH::_set_shape_coefficients is poor with residual of {fits.cost}"
            )

        if isinstance(self.rho, PyroQuantity):
            length_units = self.rho.units
        else:
            length_units = 1.0

        self.shift = fits.x[0] * units.dimensionless
        self.s_kappa = fits.x[1] * units.dimensionless
        self.dZ0dr = fits.x[2] * units.dimensionless
        self.dcndr = fits.x[3 : self.n_moments + 3] / length_units
        self.dsndr = fits.x[self.n_moments + 3 :] / length_units

        # Force dsndr[0] which has no impact on flux surface
        self.dsndr[0] = 0.0 / length_units

        self.dthetaR_dr = self.get_dthetaR_dr(self.theta, self.dcndr, self.dsndr)

    @property
    def n(self):
        return np.linspace(0, self.n_moments - 1, self.n_moments)

    @property
    def n_moments(self):
        return self._n_moments

    @n_moments.setter
    def n_moments(self, value):
        self._n_moments = value

    @property
    def delta(self):
        return np.sin(self.sn[1])

    @delta.setter
    def delta(self, value):
        self.sn[1] = np.arcsin(value)

    @property
    def s_delta(self):
        return self.dsndr[1] * np.sqrt(1 - self.delta**2) * self.rho

    @s_delta.setter
    def s_delta(self, value):
        self.dsndr[1] = value / np.sqrt(1 - self.delta**2) / self.rho

    @property
    def zeta(self):
        return -self["sn"][2]

    @zeta.setter
    def zeta(self, value):
        self["sn"][2] = -value

    @property
    def s_zeta(self):
        return -self.dsndr[2] * self.rho

    @s_zeta.setter
    def s_zeta(self, value):
        self.dsndr[2] = -value / self.rho

    def get_thetaR(self, theta):
        """

        Parameters
        ----------
        theta : Array

        Returns
        -------
        thetaR : Array
            Poloidal angle used in definition of R
        """

        if hasattr(theta, "magnitude"):
            theta = theta.m

        ntheta = np.outer(theta, self.n)

        thetaR = theta + np.sum(
            (self.cn * np.cos(ntheta) + self.sn * np.sin(ntheta)),
            axis=1,
        )

        return thetaR

    def get_dthetaR_dtheta(self, theta):
        """

        Parameters
        ----------
        theta

        Returns
        -------
        dthetaR/dtheta : Array
            theta derivative of poloidal angle used in R
        """

        if hasattr(theta, "magnitude"):
            theta = theta.m

        ntheta = np.outer(theta, self.n)

        dthetaR_dtheta = 1.0 + np.sum(
            (-self.cn * self.n * np.sin(ntheta) + self.sn * self.n * np.cos(ntheta)),
            axis=1,
        )

        return dthetaR_dtheta

    def get_d2thetaR_dtheta2(self, theta):
        """

        Parameters
        ----------
        theta

        Returns
        -------
        d^2thetaR/dtheta^2 : Array
            second theta derivative of poloidal angle used in R
        """

        if hasattr(theta, "magnitude"):
            theta = theta.m

        ntheta = np.outer(theta, self.n)

        d2thetaR_dtheta2 = -np.sum(
            ((self.n**2) * (self.cn * np.cos(ntheta) + self.sn * np.sin(ntheta))),
            axis=1,
        )

        return d2thetaR_dtheta2

    def get_dthetaR_dr(self, theta, dcndr, dsndr):
        """

        Parameters
        ----------
        theta : Array
            theta angles
        dcndr : Array
            Asymmetric coefficients in thetaR
        dsndr : Array
            Symmetric coefficients in thetaR

        Returns
        -------

        """

        if hasattr(theta, "magnitude"):
            theta = theta.m

        ntheta = np.outer(theta, self.n)

        dthetaR_dr = np.sum(
            (dcndr * np.cos(ntheta) + dsndr * np.sin(ntheta)),
            axis=1,
        )

        return dthetaR_dr

    def get_d2thetaR_drdtheta(self, theta, dcndr, dsndr):
        """

        Parameters
        ----------
        theta : Array
            theta angles
        dcndr : Array
            Asymmetric coefficients in thetaR
        dsndr : Array
            Symmetric coefficients in thetaR

        Returns
        -------

        """

        if hasattr(theta, "magnitude"):
            theta = theta.m

        ntheta = np.outer(theta, self.n)

        d2thetaR_drdtheta = np.sum(
            (-self.n * dcndr * np.sin(ntheta) + self.n * dsndr * np.cos(ntheta)),
            axis=1,
        )

        return d2thetaR_drdtheta

    def get_RZ_derivatives(
        self,
        theta: ArrayLike,
        params=None,
    ) -> np.ndarray:
        """
        Calculates the derivatives of :math:`R(r, \theta)` and :math:`Z(r, \theta)` w.r.t :math:`r` and :math:`\theta`, used in B_poloidal calc

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate grad_r on
        params : Array [Optional]
            If given then will use params = [shift, s_kappa, dZ0dr, cn[nmoments], sn[nmoments] ] when calculating
            derivatives, otherwise will use object attributes

        Returns
        -------
        dRdtheta : Array
            Derivative of :math:`R` w.r.t :math:`\theta`
        dRdr : Array
            Derivative of :math:`R` w.r.t :math:`r`
        dZdtheta : Array
            Derivative of :math:`Z` w.r.t :math:`\theta`
        dZdr : Array
            Derivative of :math:`Z` w.r.t :math:`r`
        """

        if params is None:
            shift = self.shift
            s_kappa = self.s_kappa
            dZ0dr = self.dZ0dr
            dcndr = self.dcndr
            dsndr = self.dsndr
        else:

            if isinstance(self.rho, PyroQuantity):
                length_units = self.rho.units
            else:
                length_units = 1.0

            shift = params[0] * units.dimensionless
            s_kappa = params[1] * units.dimensionless
            dZ0dr = params[2] * units.dimensionless
            dcndr = params[3 : self.n_moments + 3] / length_units
            dsndr = params[self.n_moments + 3 :] / length_units

        thetaR = self.get_thetaR(theta)
        dthetaR_dr = self.get_dthetaR_dr(theta, dcndr, dsndr)
        dthetaR_dtheta = self.get_dthetaR_dtheta(theta)

        dZdtheta = self.get_dZdtheta(theta)

        dZdr = self.get_dZdr(theta, dZ0dr, s_kappa)

        dRdtheta = self.get_dRdtheta(thetaR, dthetaR_dtheta)

        dRdr = self.get_dRdr(shift, thetaR, dthetaR_dr)

        return dRdtheta, dRdr, dZdtheta, dZdr

    def get_RZ_second_derivatives(
        self,
        theta: ArrayLike,
    ) -> np.ndarray:
        """
        Calculates the second derivatives of :math:`R(r, \theta)` and :math:`Z(r, \theta)` w.r.t :math:`r` and :math:`\theta`, used in geometry terms

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate grad_r on

        Returns
        -------
        d2Rdtheta2 : Array
                        Second derivative of :math:`R` w.r.t :math:`\theta`
        d2Rdrdtheta : Array
                        Second derivative of :math:`R` w.r.t :math:`r` and :math:`\theta`
        d2Zdtheta2 : Array
                        Second derivative of :math:`Z` w.r.t :math:`\theta`
        d2Zdrdtheta : Array
                        Second derivative of :math:`Z` w.r.t :math:`r` and :math:`\theta`
        """

        thetaR = self.get_thetaR(theta)
        dthetaR_dr = self.get_dthetaR_dr(theta, self.dcndr, self.dsndr)
        dthetaR_dtheta = self.get_dthetaR_dtheta(theta)
        d2thetaR_drdtheta = self.get_d2thetaR_drdtheta(theta, self.dcndr, self.dsndr)
        d2thetaR_dtheta2 = self.get_d2thetaR_dtheta2(theta)

        d2Zdtheta2 = self.get_d2Zdtheta2(theta)
        d2Zdrdtheta = self.get_d2Zdrdtheta(theta, self.s_kappa)
        d2Rdtheta2 = self.get_d2Rdtheta2(thetaR, dthetaR_dtheta, d2thetaR_dtheta2)
        d2Rdrdtheta = self.get_d2Rdrdtheta(
            thetaR, dthetaR_dr, dthetaR_dtheta, d2thetaR_drdtheta
        )

        return d2Rdtheta2, d2Rdrdtheta, d2Zdtheta2, d2Zdrdtheta

    def get_dZdtheta(self, theta):
        r"""
        Calculates the derivatives of :math:`Z(r, theta)` w.r.t :math:`\theta`

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate dZdtheta on

        Returns
        -------
        dZdtheta : Array
            Derivative of :math:`Z` w.r.t :math:`\theta`
        """

        return self.kappa * self.rho * np.cos(theta)

    def get_d2Zdtheta2(self, theta):
        """
        Calculates the second derivative of :math:`Z(r, theta)` w.r.t :math:`\theta`

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate dZdtheta on

        Returns
        -------
        d2Zdtheta2 : Array
            Second derivative of :math:`Z` w.r.t :math:`\theta`
        """

        return -self.kappa * self.rho * np.sin(theta)

    def get_dZdr(self, theta, dZ0dr, s_kappa):
        r"""
        Calculates the derivatives of :math:`Z(r, \theta)` w.r.t :math:`r`

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate dZdr on
        dZ0dr : Float
            Derivative in midplane elevation
        s_kappa : Float
            Shear in Elongation :math:`r/\kappa \partial \kappa/\partial r`

        Returns
        -------
        dZdr : Array
            Derivative of :math:`Z` w.r.t :math:`r`
        """
        return dZ0dr + self.kappa * np.sin(theta) * (1 + s_kappa)

    def get_d2Zdrdtheta(self, theta, s_kappa):
        r"""
        Calculates the second derivative of :math:`Z(r, \theta)` w.r.t :math:`r` and :math:`\theta`

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate dZdr on
        s_kappa : Float
            Shear in Elongation :math:`r/\kappa \partial \kappa/\partial r`

        Returns
        -------
        d2Zdrdtheta : Array
            Second derivative of :math:`Z` w.r.t :math:`r` and :math:`\theta`
        """
        return self.kappa * np.cos(theta) * (1 + s_kappa)

    def get_dRdtheta(self, thetaR, dthetaR_dtheta):
        """
        Calculates the derivatives of :math:`R(r, \theta)` w.r.t :math:`\theta`

        Parameters
        ----------
        thetaR: ArrayLike
            Array of thetaR points to evaluate dRdtheta on
        dthetaR_dtheta : ArrayLike
            Theta derivative of thetaR
        -------
        dRdtheta : Array
            Derivative of :math:`R` w.r.t :math:`\theta`
        """

        return -self.rho * np.sin(thetaR) * dthetaR_dtheta

    def get_d2Rdtheta2(self, thetaR, dthetaR_dtheta, d2thetaR_dtheta2):
        """
        Calculates the second derivative of :math:`R(r, \theta)` w.r.t :math:`\theta`

        Parameters
        ----------
        thetaR: ArrayLike
            Array of thetaR points to evaluate dRdtheta on
        dthetaR_dtheta : ArrayLike
            Theta derivative of thetaR
        d2thetaR_dtheta2 : ArrayLike
            Second theta derivative of thetaR
        -------
        d2Rdtheta2 : Array
            Second derivative of :math:`R` w.r.t :math:`\theta`
        """

        return -self.rho * np.sin(thetaR) * d2thetaR_dtheta2 - self.rho * (
            dthetaR_dtheta**2
        ) * np.cos(thetaR)

    def get_dRdr(self, shift, thetaR, dthetaR_dr):
        r"""
        Calculates the derivatives of :math:`R(r, \theta)` w.r.t :math:`r`

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate dRdr on
        shift : Float
            Shafranov shift
        thetaR: ArrayLike
            Array of thetaR points to evaluate dRdtheta on
        dthetaR_dr : ArrayLike
            Radial derivative of thetaR

        Returns
        -------
        dRdr : Array
            Derivative of :math:`R` w.r.t :math:`r`
        """
        return shift + np.cos(thetaR) - self.rho * np.sin(thetaR) * dthetaR_dr

    def get_d2Rdrdtheta(self, thetaR, dthetaR_dr, dthetaR_dtheta, d2thetaR_drdtheta):
        """
        Calculate the second derivative of :math:`R(r, \theta)` w.r.t :math:`r` and :math:`\theta`

        Parameters
        ----------
        theta: ArrayLike
            Array of theta points to evaluate dRdr on
        thetaR: ArrayLike
            Array of thetaR points to evaluate dRdtheta on
        dthetaR_dr : ArrayLike
            Radial derivative of thetaR
        dthetaR_dtheta : ArrayLike
            Theta derivative of thetaR
        d2thetaR_drdtheta : ArrayLike
            Second derivative of thetaR w.r.t :math:`r` and :math:`\theta`

        Returns
        -------
        d2Rdrdtheta : Array
            Second derivative of R w.r.t :math:`r` and :math:`\theta`
        """
        return -dthetaR_dtheta * np.sin(thetaR) - self.rho * (
            np.sin(thetaR) * d2thetaR_drdtheta
            + dthetaR_dr * dthetaR_dtheta * np.cos(thetaR)
        )

    def get_flux_surface(
        self,
        theta: ArrayLike,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates (R,Z) of a flux surface given a set of MXH fits

        Parameters
        ----------
        theta : Array
            Values of theta to evaluate flux surface

        Returns
        -------
        R : Array
            R values for this flux surface (if not normalised then in [m])
        Z : Array
            Z Values for this flux surface (if not normalised then in [m])
        """

        thetaR = self.get_thetaR(theta)

        R = self.Rmaj + self.rho * np.cos(thetaR)
        Z = self.Z0 + self.kappa * self.rho * np.sin(theta)

        return R, Z

    def default(self):
        """
        Default parameters for geometry
        Same as GA-STD case
        """
        super(LocalGeometryMXH, self).__init__(default_mxh_inputs())

    def _generate_shape_coefficients_units(self, norms):
        """
        Need to change dcndr and dsndr to pyro norms
        """
        return {
            "kappa": units.dimensionless,
            "s_kappa": units.dimensionless,
            "cn": units.dimensionless,
            "sn": units.dimensionless,
            "shift": units.dimensionless,
            "dZ0dr": units.dimensionless,
            "dcndr": norms.lref**-1,
            "dsndr": norms.lref**-1,
            "dthetaR_dr": norms.lref**-1,
        }

    @staticmethod
    def _shape_coefficient_names():
        """
        List of shape coefficient names used for printing
        """
        return [
            "kappa",
            "s_kappa",
            "cn",
            "sn",
            "shift",
            "dZ0dr",
            "dcndr",
            "dsndr",
        ]

    def from_local_geometry(
        self, local_geometry, verbose=False, show_fit=False, **kwargs
    ):
        r"""
        Loads LocalGeometry object of one type from a LocalGeometry Object of a different type

        Miller is a special case which is a subset of MXH so we can directly set values
        Parameters
        ----------
        local_geometry : LocalGeometry
            LocalGeometry object
        verbose : Boolean
            Controls verbosity

        """

        if not isinstance(local_geometry, LocalGeometry):
            raise ValueError(
                "Input to from_local_geometry must be of type LocalGeometry"
            )

        if local_geometry.local_geometry == "Miller":
            self.psi_n = local_geometry.psi_n
            self.rho = local_geometry.rho
            self.Rmaj = local_geometry.Rmaj
            self.a_minor = local_geometry.a_minor
            self.Fpsi = local_geometry.Fpsi
            self.B0 = local_geometry.B0
            self.Z0 = local_geometry.Z0
            self.q = local_geometry.q
            self.shat = local_geometry.shat
            self.beta_prime = local_geometry.beta_prime

            self.R_eq = local_geometry.R_eq
            self.Z_eq = local_geometry.Z_eq
            self.theta_eq = local_geometry.theta
            self.b_poloidal_eq = local_geometry.b_poloidal_eq

            self.R = local_geometry.R
            self.Z = local_geometry.Z
            self.theta = local_geometry.theta

            self.dpsidr = local_geometry.dpsidr

            self.ip_ccw = local_geometry.ip_ccw
            self.bt_ccw = local_geometry.bt_ccw

            # Fix units here of shaping gradients
            self.dcndr *= 1 / local_geometry.rho.units
            self.dsndr *= 1 / local_geometry.rho.units

            self.kappa = local_geometry.kappa
            self.s_kappa = local_geometry.s_kappa

            self.delta = local_geometry.delta
            self.s_delta = local_geometry.s_delta

            self.shift = local_geometry.shift
            self.dZ0dr = local_geometry.dZ0dr

            self.dRdtheta = local_geometry.dRdtheta
            self.dRdr = local_geometry.dRdr
            self.dZdtheta = local_geometry.dZdtheta
            self.dZdr = local_geometry.dZdr

            self.dthetaR_dr = self.get_dthetaR_dr(self.theta, self.dcndr, self.dsndr)

            # Bunit for GACODE codes
            self.bunit_over_b0 = local_geometry.get_bunit_over_b0()

            if show_fit:
                self.plot_equilibrium_to_local_geometry_fit(show_fit=True)

        else:
            super().from_local_geometry(local_geometry, show_fit=show_fit, **kwargs)
