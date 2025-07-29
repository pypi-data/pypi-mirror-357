from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
from warnings import warn

import numpy as np
from scipy.integrate import quad

from ..constants import pi
from ..decorators import not_implemented
from ..equilibrium import Equilibrium
from ..factory import Factory
from ..typing import ArrayLike
from ..units import ureg as units

if TYPE_CHECKING:
    import matplotlib.pyplot as plt

    from ..normalisation import SimulationNormalisation as Normalisation


def default_inputs():
    # Return default args to build a LocalGeometry
    # Uses a function call to avoid the user modifying these values
    return {
        "psi_n": 0.5,
        "rho": 0.5,
        "Rmaj": 3.0,
        "Z0": 0.0,
        "a_minor": 1.0,
        "Fpsi": 0.0,
        "B0": None,
        "q": 2.0,
        "shat": 1.0,
        "beta_prime": 0.0,
        "dpsidr": 1.0,
        "bt_ccw": -1,
        "ip_ccw": -1,
    }


class LocalGeometry:
    r"""
    General geometry Object representing local LocalGeometry fit parameters

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
        :math:`\partial \psi / \partial r`
    q : Float
        Safety factor
    shat : Float
        Magnetic shear :math:`r/q \partial q/ \partial r`
    beta_prime : Float
        :math:`\beta = 2 \mu_0 \partial p \partial \rho 1/B0^2`

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
    """

    def __init__(self, *args, **kwargs):

        self._already_warned = False

        s_args = list(args)
        if args and isinstance(s_args[0], dict):
            for key, value in s_args[0].items():
                setattr(self, key, value)

        elif len(args) == 0:
            self.local_geometry = None

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __setattr__(self, key, value):
        if value is None:
            super().__setattr__(key, value)

        if hasattr(self, key):
            attr = getattr(self, key)
            if hasattr(attr, "units") and not hasattr(value, "units"):
                value *= attr.units
                if not self._already_warned and str(attr.units) != "dimensionless":
                    warn(
                        f"missing unit from {key}, adding {attr.units}. To suppress this warning, specify units. Will "
                        f"maintain units if not specified from now on"
                    )
                    self._already_warned = True
        super().__setattr__(key, value)

    def keys(self):
        return self.__dict__.keys()

    def from_global_eq(
        self,
        eq: Equilibrium,
        psi_n: float,
        norms: Normalisation,
        show_fit=False,
        **kwargs,
    ):
        """
        Loads LocalGeometry object from an Equilibrium Object
        """

        # TODO FluxSurface is COCOS 11, this uses something else. Here we switch from
        # a clockwise theta grid to a counter-clockwise one, and divide any psi
        # quantities by 2 pi
        fs = eq.flux_surface(psi_n=psi_n)
        # Convert to counter-clockwise, discard repeated endpoint
        R = fs["R"].data[:0:-1]
        Z = fs["Z"].data[:0:-1]
        b_poloidal = fs["B_poloidal"].data[:0:-1]

        R_major = fs.R_major
        rho = fs.r_minor
        Zmid = fs.Z_mid

        Fpsi = fs.F
        B0 = Fpsi / R_major
        FF_prime = fs.FF_prime * (2 * np.pi)

        dpsidr = fs.psi_gradient / (2 * np.pi)
        q = fs.q
        shat = fs.magnetic_shear

        if "lref_major_radius" in str(norms.default_convention.lref):
            lref = fs.R_major
        elif "lref_minor_radius" in str(norms.default_convention.lref):
            lref = fs.a_minor
        elif "lref_magnetic_axis" in str(norms.default_convention.lref):
            lref = eq.R_axis

        dpressure_drho = fs.pressure_gradient * lref

        # beta_prime needs special treatment...
        beta_prime = (2 * units.mu0 * dpressure_drho / B0**2).to_base_units().m

        # Store Equilibrium values
        self.psi_n = psi_n
        self.rho = rho
        self.Rmaj = R_major
        self.Z0 = Zmid
        self.a_minor = fs.a_minor
        self.Fpsi = Fpsi
        self.FF_prime = FF_prime
        self.B0 = abs(B0)
        self.q = q
        self.shat = shat
        self.beta_prime = beta_prime
        self.dpsidr = dpsidr

        self.ip_ccw = np.sign(q / B0)
        self.bt_ccw = np.sign(B0)

        self.R_eq = R
        self.Z_eq = Z
        self.b_poloidal_eq = b_poloidal

        # Calculate shaping coefficients
        self._set_shape_coefficients(self.R_eq, self.Z_eq, self.b_poloidal_eq, **kwargs)

        self.b_poloidal = self.get_b_poloidal(
            theta=self.theta,
        )
        self.dRdtheta, self.dRdr, self.dZdtheta, self.dZdr = self.get_RZ_derivatives(
            self.theta
        )
        self.jacob = self.R * (self.dRdr * self.dZdtheta - self.dZdr * self.dRdtheta)

        # Bunit for GACODE codes
        self.bunit_over_b0 = self.get_bunit_over_b0()

        if show_fit:
            self.plot_equilibrium_to_local_geometry_fit(show_fit=True)

        # Set references and normalise
        norms.set_bref(self)
        norms.set_lref(self)
        self.normalise(norms)

    def from_local_geometry(
        self, local_geometry, verbose=False, show_fit=False, **kwargs
    ):
        r"""
        Loads LocalGeometry object of one type from a LocalGeometry Object of a different type

        Gradients in shaping parameters are fitted from poloidal field

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

        # Load in parameters that
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
        self.dpsidr = local_geometry.dpsidr

        self.ip_ccw = local_geometry.ip_ccw
        self.bt_ccw = local_geometry.bt_ccw

        self._set_shape_coefficients(
            self.R_eq, self.Z_eq, self.b_poloidal_eq, verbose, **kwargs
        )

        self.b_poloidal = self.get_b_poloidal(
            theta=self.theta,
        )
        self.dRdtheta, self.dRdr, self.dZdtheta, self.dZdr = self.get_RZ_derivatives(
            self.theta
        )

        # Bunit for GACODE codes
        self.bunit_over_b0 = self.get_bunit_over_b0()

        if show_fit:
            self.plot_equilibrium_to_local_geometry_fit(show_fit=True)

    @classmethod
    def from_gk_data(cls, params: Dict[str, Any]):
        """
        Initialise from data gathered from GKCode object, and additionally set
        bunit_over_b0
        """
        # TODO change __init__ to take necessary parameters by name. It shouldn't
        # be possible to have a local_geometry object that does not contain all attributes.
        # bunit_over_b0 should be an optional argument, and the following should
        # be performed within __init__ if it is None
        local_geometry = cls(params)

        # Values are not yet normalised
        local_geometry.bunit_over_b0 = local_geometry.get_bunit_over_b0()

        # Get dpsidr from Bunit/B0
        local_geometry.dpsidr = (
            local_geometry.bunit_over_b0 / local_geometry.q * local_geometry.rho
        )

        # This is arbitrary, maybe should be a user input
        local_geometry.theta = np.linspace(0, 2 * pi, 256)

        local_geometry.R, local_geometry.Z = local_geometry.get_flux_surface(
            local_geometry.theta
        )
        local_geometry.b_poloidal = local_geometry.get_b_poloidal(
            theta=local_geometry.theta,
        )

        #  Fitting R_eq, Z_eq, and b_poloidal_eq need to be defined from local parameters
        local_geometry.R_eq = local_geometry.R
        local_geometry.Z_eq = local_geometry.Z
        local_geometry.b_poloidal_eq = local_geometry.b_poloidal

        (
            local_geometry.dRdtheta,
            local_geometry.dRdr,
            local_geometry.dZdtheta,
            local_geometry.dZdr,
        ) = local_geometry.get_RZ_derivatives(local_geometry.theta)

        return local_geometry

    def normalise(self, norms):
        """
        Convert LocalGeometry Parameters to current NormalisationConvention
        Note this creates the attribute unit_mapping which is used to apply
        units to the LocalGeometry object
        Parameters
        ----------
        norms : SimulationNormalisation
            Normalisation convention to convert to

        """
        self._generate_local_geometry_units(norms)

        for key, val in self.unit_mapping.items():
            if val is None:
                continue

            if not hasattr(self, key):
                continue

            attribute = getattr(self, key)

            if hasattr(attribute, "units"):
                new_attr = attribute.to(val, norms.context)
            elif attribute is not None:
                new_attr = attribute * val

            setattr(self, key, new_attr)

    def _generate_local_geometry_units(self, norms):
        """
        Generate dictionary for the different units of each attribute

        Parameters
        ----------
        norms

        Returns
        -------

        """
        general_units = {
            "psi_n": units.dimensionless,
            "rho": norms.lref,
            "Rmaj": norms.lref,
            "a_minor": norms.lref,
            "Z0": norms.lref,
            "B0": norms.bref,
            "q": units.dimensionless,
            "shat": units.dimensionless,
            "Fpsi": norms.bref * norms.lref,
            "FF_prime": norms.bref,
            "dRdtheta": norms.lref,
            "dZdtheta": norms.lref,
            "dRdr": units.dimensionless,
            "dZdr": units.dimensionless,
            "dpsidr": norms.lref * norms.bref,
            "jacob": norms.lref**2,
            "R": norms.lref,
            "Z": norms.lref,
            "b_poloidal": norms.bref,
            "R_eq": norms.lref,
            "Z_eq": norms.lref,
            "b_poloidal_eq": norms.bref,
            "beta_prime": norms.bref**2 / norms.lref,
            "bunit_over_b0": units.dimensionless,
            "bt_ccw": units.dimensionless,
            "ip_ccw": units.dimensionless,
        }

        # Make shape specific units
        shape_specific_units = self._generate_shape_coefficients_units(norms)

        self.unit_mapping = {**general_units, **shape_specific_units}

    @not_implemented
    def _set_shape_coefficients(self, R, Z, b_poloidal, verbose=False):
        r"""
        Calculates LocalGeometry shaping coefficients from R, Z and b_poloidal

        Parameters
        ----------
        R : Array
            R for the given flux surface
        Z : Array
            Z for the given flux surface
        b_poloidal : Array
            `b_\theta` for the given flux surface
        verbose : Boolean
            Controls verbosity
        """

        pass

    @not_implemented
    def _generate_shape_coefficients_units(self, norms):
        """
        Converts shaping coefficients to current normalisation
        Parameters
        ----------
        norms

        Returns
        -------

        """
        pass

    @not_implemented
    def get_RZ_derivatives(self, params=None):
        pass

    def get_grad_r(
        self,
        theta: ArrayLike,
        params=None,
    ) -> np.ndarray:
        """
        MXH definition of grad r from
        MXH, R. L., et al. "Noncircular, finite aspect ratio, local equilibrium model."
        Physics of Plasmas 5.4 (1998): 973-978.

        Also see eqn 39 in Candy Plasma Phys. Control. Fusion 51 (2009) 105009


        Parameters
        ----------
        kappa: Scalar
            elongation
        shift: Scalar
            Shafranov shift
        theta: ArrayLike
            Array of theta points to evaluate grad_r on

        Returns
        -------
        grad_r : Array
            grad_r(theta)
        """

        dRdtheta, dRdr, dZdtheta, dZdr = self.get_RZ_derivatives(theta, params)

        g_tt = dRdtheta**2 + dZdtheta**2

        grad_r = np.sqrt(g_tt) / (dRdr * dZdtheta - dRdtheta * dZdr)

        return grad_r

    def minimise_b_poloidal(self, params, even_space_theta=False):
        """
        Function for least squares minimisation of poloidal field

        Parameters
        ----------
        params : List
            List with LocalGeometry type specific values

        Returns
        -------
        Difference between local geometry and equilibrium get_b_poloidal

        """

        if even_space_theta:
            b_poloidal_eq = self.b_poloidal_even_space
        else:
            b_poloidal_eq = self.b_poloidal_eq
        result = (
            b_poloidal_eq - self.get_b_poloidal(theta=self.theta, params=params)
        ).m
        return result

    def get_b_poloidal(self, theta: ArrayLike, params=None) -> np.ndarray:
        r"""
        Returns Miller prediction for get_b_poloidal given flux surface parameters

        Parameters
        ----------
        params : List
            List with LocalGeometry type specific values

        Returns
        -------
        local_geometry_b_poloidal : Array
            Array of get_b_poloidal from Miller fit
        """

        R, Z = self.get_flux_surface(theta)

        return np.abs(self.dpsidr) / R * self.get_grad_r(theta, params)

    def get_dLdtheta(self, theta):
        """
        Returns dLdtheta used in loop integrals

        See eqn 93 in Candy Plasma Phys. Control. Fusion 51 (2009) 105009

        Parameters
        ----------
        theta : ArrayLike
            Poloidal angle to evaluate at

        Returns
        -------
        dLdtheta : Poloidal derivative of Arclength
        """

        dRdtheta, dRdr, dZdtheta, dZdr = self.get_RZ_derivatives(theta)

        return np.sqrt(dRdtheta**2 + dZdtheta**2)

    def get_bunit_over_b0(self):
        r"""
        Get Bunit/B0 using q and loop integral of Bp

        :math:`\frac{B_{unit}}{B_0} = \frac{R_0}{2\pi r_{minor}} \oint \frac{a}{R} \frac{dl_N}{\nabla r}`

        where :math:`dl_N = \frac{dl}{a_{minor}}` coming from the normalising a_minor

        See eqn 97 in Candy Plasma Phys. Control. Fusion 51 (2009) 105009

        Returns
        -------
        bunit_over_b0 : Float
             :math:`\frac{B_{unit}}{B_0}`

        """

        def bunit_integrand(theta):
            R, _ = self.get_flux_surface(theta)
            R_grad_r = R * self.get_grad_r(theta)
            dLdtheta = self.get_dLdtheta(theta)
            # Expect dimensionless quantity
            result = units.Quantity(dLdtheta / R_grad_r).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        integral = quad(bunit_integrand, 0.0, 2 * np.pi)[0]

        return integral * self.Rmaj / (2 * pi * self.rho)

    def get_f_psi(self):
        r"""
        Calculate safety factor from b poloidal field, R, Z and q
        :math:`f = \frac{2\pi q}{\oint \frac{dl}{R^2 B_{\theta}}}`

        See eqn 97 in Candy Plasma Phys. Control. Fusion 51 (2009) 105009

        Returns
        -------
        f : Float
            Prediction for :math:`f_\psi` from B_poloidal
        """

        def f_psi_integrand(theta):
            R, _ = self.get_flux_surface(theta)
            b_poloidal = self.get_b_poloidal(theta)
            dLdtheta = self.get_dLdtheta(theta)
            result = units.Quantity(dLdtheta / (R**2 * b_poloidal)).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        bref = self.b_poloidal.units
        lref = self.R.units

        @units.wraps(bref**-1 * lref**-1, (), False)
        def get_integral():
            return quad(f_psi_integrand, 0.0, 2 * np.pi)[0]

        integral = get_integral()
        q = self.q

        return 2 * pi * q / integral

    def get_flux_surface_area_volume(self):
        r"""
        Calculate the poloidal and toroidal area of the flux surface
        and the toroidal volume in units of lref

        :math:`A_{toroidal} = 2\pi \int_0^{2\pi}  R\frac{\partial L}{\partial \theta} d\theta`

        :math:`A_{poloidal} = \int_0^{2\pi}  R\frac{\partial Z}{\partial \theta} d\theta`

        :math:`V_{toroidal} = \pi \ int_0^{2\pi}  R^2\frac{\partial Z}{\partial \theta} d\theta`

        Returns
        -------
        poloidal_area : float, units [lref**2]
            Calculation of the poloidal surface area  :math:`A_{poloidal}`
        toroidal_area : float, units [lref**2]
            Calculation of the toroidal surface area  :math:`A_{toroidal}`
        toroidal_volume : float, units [lref**3]
            Calculation of the poloidal volume :math:`V_{toroidal}`
        """

        lref = self.R.units

        # Calculate using Green's theorem
        def poloidal_surface_integrand(theta):
            R, _ = self.get_flux_surface(theta)
            (
                _,
                _,
                dZdtheta,
                _,
            ) = self.get_RZ_derivatives(theta)
            # Expect dimensionless quantity
            result = units.Quantity(R * dZdtheta).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        @units.wraps(lref**2, (), False)
        def poloidal_surface_integral():
            return quad(poloidal_surface_integrand, 0.0, 2 * np.pi)[0]

        # Calculate using line integral * 2pi R
        def toroidal_surface_integrand(theta):
            R, _ = self.get_flux_surface(theta)
            dLdtheta = self.get_dLdtheta(theta)
            # Expect dimensionless quantity
            result = units.Quantity(R * dLdtheta).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        @units.wraps(lref**2, (), False)
        def toroidal_surface_integral():
            return 2.0 * np.pi * quad(toroidal_surface_integrand, 0.0, 2 * np.pi)[0]

        # Calculate using Harry's suggestion
        def toroidal_volume_integrand(theta):
            R, Z = self.get_flux_surface(theta)
            (
                _,
                _,
                dZdtheta,
                _,
            ) = self.get_RZ_derivatives(theta)
            # Expect dimensionless quantity
            result = units.Quantity((R**2 * dZdtheta)).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        @units.wraps(lref**3, (), False)
        def toroidal_volume_integral():
            return np.pi * quad(toroidal_volume_integrand, 0.0, 2 * np.pi)[0]

        poloidal_area = poloidal_surface_integral()
        toroidal_area = toroidal_surface_integral()
        toroidal_volume = toroidal_volume_integral()

        return poloidal_area, toroidal_area, toroidal_volume

    def get_flux_surface_area_volume_derivatives(self):
        r"""
        Calculate the derivative of the poloidal and toroidal
        area of the flux surface and the toroidal volume with respect to
        r

        :math:`\frac{\partial A_{toroidal}}{\partial r} = 2\pi \int_0^{2\pi}  R\frac{\partial L}{\partial \theta} d\theta`

        :math:`\frac{\partial A_{poloidal}}{\partial r} = \int_0^{2\pi} \frac{J}{R} d\theta`

        :math:`V_{toroidal} = 2\pi \ int_0^{2\pi} J d\theta`

        Returns
        -------
        poloidal_area : float, units [lref**2]
            Calculation of the poloidal surface area  :math:`A_{poloidal}`
        toroidal_area : float, units [lref**2]
            Calculation of the toroidal surface area  :math:`A_{toroidal}`
        toroidal_volume : float, units [lref**3]
            Calculation of the poloidal volume :math:`V_{toroidal}`
        """

        lref = self.R.units

        # Calculate using Green's theorem
        def poloidal_surface_derivative_integrand(theta):
            (
                dRdtheta,
                dRdr,
                dZdtheta,
                dZdr,
            ) = self.get_RZ_derivatives(theta)
            # Expect dimensionless quantity
            result = units.Quantity(dRdr * dZdtheta - dZdr * dRdtheta).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        @units.wraps(lref, (), False)
        def poloidal_surface_derivative_integral():
            return quad(poloidal_surface_derivative_integrand, 0.0, 2 * np.pi)[0]

        # Calculate using line integral * 2pi R
        def toroidal_surface_derivative_integrand(theta):
            R, _ = self.get_flux_surface(theta)
            (
                dRdtheta,
                dRdr,
                dZdtheta,
                dZdr,
            ) = self.get_RZ_derivatives(theta)
            (
                d2Rdtheta2,
                d2Rdrdtheta,
                d2Zdtheta2,
                d2Zdrdtheta,
            ) = self.get_RZ_second_derivatives(theta)
            g_tt = dRdtheta**2 + dZdtheta**2

            integrand = dRdr * np.sqrt(g_tt) + R / np.sqrt(g_tt) * (
                dRdtheta * d2Rdrdtheta + dZdtheta * d2Zdrdtheta
            )
            # Expect dimensionless quantity
            result = units.Quantity(integrand).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        @units.wraps(lref, (), False)
        def toroidal_surface_derivative_integral():
            return (
                2.0
                * np.pi
                * quad(toroidal_surface_derivative_integrand, 0.0, 2 * np.pi)[0]
            )

        # Calculate using Harry's suggestion
        def toroidal_volume_derivative_integrand(theta):
            R, _ = self.get_flux_surface(theta)
            (
                dRdtheta,
                dRdr,
                dZdtheta,
                dZdr,
            ) = self.get_RZ_derivatives(theta)
            Jacobian = R * (dRdr * dZdtheta - dZdr * dRdtheta)
            # Expect dimensionless quantity
            result = units.Quantity(Jacobian).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        @units.wraps(lref**2, (), False)
        def toroidal_volume_derivative_integral():
            return (
                2
                * np.pi
                * quad(toroidal_volume_derivative_integrand, 0.0, 2 * np.pi)[0]
            )

        poloidal_area_derivative = poloidal_surface_derivative_integral()
        toroidal_area_derivative = toroidal_surface_derivative_integral()
        toroidal_volume_derivative = toroidal_volume_derivative_integral()

        return (
            poloidal_area_derivative,
            toroidal_area_derivative,
            toroidal_volume_derivative,
        )

    def test_safety_factor(self):
        r"""
        Calculate safety factor from LocalGeometry object b poloidal field
        :math:`q = \frac{1}{2\pi} \oint \frac{f dl}{R^2 B_{\theta}}`

        Returns
        -------
        q : Float
            Prediction for :math:`q` from fourier B_poloidal
        """

        def q_integrand(theta):
            R, _ = self.get_flux_surface(theta)
            b_poloidal = self.get_b_poloidal(theta)
            dLdtheta = self.get_dLdtheta(theta)
            result = units.Quantity(dLdtheta / (R**2 * b_poloidal)).magnitude
            # Avoid SciPy warning when returning array with a single element
            if np.ndim(result) == 1 and np.size(result) == 1:
                result = result[0]
            return result

        f_psi = self.Fpsi
        bref = self.b_poloidal.units
        lref = self.R.units

        @units.wraps(bref**-1 * lref**-1, (), False)
        def get_integral():
            return quad(q_integrand, 0.0, 2 * np.pi)[0]

        integral = get_integral()

        return integral * f_psi / (2 * pi)

    def plot_equilibrium_to_local_geometry_fit(
        self, axes: Optional[Tuple[plt.Axes, plt.Axes]] = None, show_fit=False
    ):
        import matplotlib.pyplot as plt

        # Get flux surface and b_poloidal
        R_fit, Z_fit = self.get_flux_surface(theta=self.theta)

        bpol_fit = self.get_b_poloidal(
            theta=self.theta,
        )

        # Set up plot if one doesn't exist already
        if axes is None:
            fig, axes = plt.subplots(1, 2)
        else:
            fig = axes[0].get_figure()

        # Plot R, Z
        axes[0].plot(self.R_eq.m, self.Z_eq.m, label="Data")
        axes[0].plot(R_fit.m, Z_fit.m, "--", label="Fit")
        axes[0].set_xlabel("R")
        axes[0].set_ylabel("Z")
        axes[0].set_aspect("equal")
        axes[0].set_title(f"Fit to flux surface for {self.local_geometry}")
        axes[0].legend()
        axes[0].grid()

        # Plot Bpoloidal
        axes[1].plot(self.theta_eq.m, self.b_poloidal_eq.m, label="Data")
        axes[1].plot(self.theta.m, bpol_fit.m, "--", label="Fit")
        axes[1].legend()
        axes[1].set_xlabel("theta")
        axes[1].set_title(f"Fit to poloidal field for {self.local_geometry}")
        axes[1].set_ylabel("Bpol")
        axes[1].grid()

        if show_fit:
            plt.show()
        else:
            return fig, axes

    def __repr__(self):
        str_list = [f"{type(self)}(\n" f"type  = {self.local_geometry},\n"]
        str_list.extend(
            [f"{k} = {getattr(self, k)}\n" for k in default_inputs().keys()]
        )
        str_list.extend(
            [f"{k} = {getattr(self, k)}\n" for k in self._shape_coefficient_names()]
        )
        str_list.extend([f"bunit_over_b0 = {self.bunit_over_b0}"])

        return "".join(str_list)


# Create global factory for LocalGeometry objects
local_geometry_factory = Factory(super_class=LocalGeometry)
