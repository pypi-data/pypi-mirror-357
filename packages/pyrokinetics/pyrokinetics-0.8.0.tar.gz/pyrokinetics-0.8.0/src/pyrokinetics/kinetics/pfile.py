"""
Reads in an Osborne pFile: https://omfit.io/_modules/omfit_classes/omfit_osborne.html#OMFITosborneProfile


"""

import re
import warnings
from contextlib import redirect_stdout
from textwrap import dedent

import numpy as np
from freeqdsk import peqdsk

from ..constants import deuterium_mass, electron_mass
from ..equilibrium import Equilibrium
from ..file_utils import FileReader
from ..species import Species
from ..typing import PathLike
from ..units import UnitSpline
from ..units import ureg as units
from .kinetics import Kinetics


def ion_species_selector(nucleons, charge):
    """
    Returns ion species type from:

    hydrogen deuterium, tritium, helium3, helium, other impurity.

    Might need to update with more specific masses, such as 6.94 for Li-7, etc.
    """
    if nucleons == 1:
        if charge.m == 1:
            return "hydrogen"
        else:
            print(
                "You have a species with a single nucleon which is not a proton. Strange. Returning neutron for now. \n"
            )
            return "neutron"
    if nucleons == 2 and charge.m == 1:
        return "deuterium"
    elif nucleons == 4 and charge.m == 2:
        return "helium"
    elif nucleons == 3:
        if charge.m == 1:
            return "tritium"
        if charge.m == 2:
            return "helium3"
    elif nucleons == 6 and charge.m == 3:
        return "lithium"
    elif (1.0 < nucleons < 3.0) and charge.m == 1:
        return "hydrogenic"
    else:
        return "impurity"


def np_to_T(n, p):
    """
    n is in m^{-3}, T is in eV, p is in Pascals.
    Returns temperature in eV.
    """
    if np.any(n.magnitude == 0):
        warnings.warn(
            "Division by zero (density) encountered when calculating temperature. "
            "Returning temperature of 0 eV for these elements.",
            UserWarning,
        )
    return np.divide(p, n, out=np.zeros_like(p), where=(n != 0)).to("eV")


class KineticsReaderpFile(FileReader, file_type="pFile", reads=Kinetics):
    def read_from_file(self, filename: PathLike, eq: Equilibrium = None) -> Kinetics:
        """
        Reads in Osborne pFile. Your pFile should just be called, pFile.
        Also reads a geqdsk file via eq_file to obtain r/a.
        """

        # Use Equilibrium to obtain rho_func.
        if eq is None:
            raise ValueError(
                dedent(
                    f"""\
                    {self.__class__.__name__} must be provided with an Equilibrium object via
                    the keyword argument 'eq'. Please load an Equilibrium.
                    """
                )
            )

        # Read pFile, get generic data.
        with redirect_stdout(None), open(filename) as f:
            data = peqdsk.read(f)

        profiles = data["profiles"]
        species = data["species"]

        # Interpolate on psi_n.
        te_psi_n = profiles["te"]["psinorm"] * units.dimensionless
        electron_temp_data = profiles["te"]["data"] * 1e3 * units.eV
        electron_temp_func = UnitSpline(te_psi_n, electron_temp_data)

        ne_psi_n = profiles["ne"]["psinorm"] * units.dimensionless
        electron_dens_data = profiles["ne"]["data"] * 1e20 * units.meter**-3
        electron_dens_func = UnitSpline(ne_psi_n, electron_dens_data)

        rho_g = eq["r_minor"].data.magnitude
        rho_g = rho_g / rho_g[-1] * units.lref_minor_radius
        psi_n_g = eq["psi_n"].data
        rho_func = UnitSpline(psi_n_g, rho_g)

        unit_charge_array = np.ones(len(ne_psi_n))

        if "omeg" in profiles.keys():
            omega_psi_n = profiles["omeg"]["psinorm"] * units.dimensionless
            omega_data = profiles["omeg"]["data"] * 1e3 * units.radians / units.second
        else:
            omega_psi_n = te_psi_n * units.dimensionless
            omega_data = (
                np.zeros(len(omega_psi_n), dtype="float") * units.radians / units.second
            )

        omega_func = UnitSpline(omega_psi_n, omega_data)

        electron_charge = UnitSpline(
            ne_psi_n, -1 * unit_charge_array * units.elementary_charge
        )

        electron = Species(
            species_type="electron",
            charge=electron_charge,
            mass=electron_mass,
            dens=electron_dens_func,
            temp=electron_temp_func,
            omega0=omega_func,
            rho=rho_func,
        )

        result = {"electron": electron}
        num_ions = len(species)

        # Check whether fast particles.
        try:
            if np.all(profiles["nb"]["data"] == 0.0):
                fast_particle = 0
            else:
                fast_particle = 1
        except KeyError:
            fast_particle = 0

        num_thermal_ions = num_ions - fast_particle

        # thermal ions have same temperature in pFile.
        ti_psi_n = profiles["ti"]["psinorm"] * units.dimensionless
        ion_temp_data = profiles["ti"]["data"] * 1e3 * units.eV
        ion_temp_func = UnitSpline(ti_psi_n, ion_temp_data)

        for ion_it in np.arange(num_thermal_ions):
            if ion_it == num_thermal_ions - 1:
                ni_psi_n = profiles["ni"]["psinorm"] * units.dimensionless
                ion_dens_data = profiles["ni"]["data"] * 1e20 * units.meter**-3
                ion_dens_func = UnitSpline(ni_psi_n, ion_dens_data)

                ion_charge = species[ion_it]["Z"] * units.elementary_charge
                ion_nucleons = species[ion_it]["A"]
                ion_mass = ion_nucleons * deuterium_mass / 2.0

                species_name = ion_species_selector(ion_nucleons, ion_charge)

                result[species_name] = Species(
                    species_type=species_name,
                    charge=UnitSpline(ne_psi_n, ion_charge * unit_charge_array),
                    mass=ion_mass,
                    dens=ion_dens_func,
                    temp=ion_temp_func,
                    omega0=omega_func,
                    rho=rho_func,
                )

            else:
                try:
                    nz_psi_n = (
                        profiles[f"nz{ion_it+1}"]["psinorm"] * units.dimensionless
                    )
                    impurity_dens_data = (
                        profiles[f"nz{ion_it+1}"]["data"] * 1e20 * units.meter**-3
                    )
                except KeyError:
                    nz_psi_n = ni_psi_n
                    impurity_dens_data = ion_dens_data * 0.0

                impurity_dens_func = UnitSpline(nz_psi_n, impurity_dens_data)

                impurity_charge = species[ion_it]["Z"] * units.elementary_charge
                impurity_nucleons = species[ion_it]["A"]
                impurity_mass = impurity_nucleons * deuterium_mass / 2.0

                species_name = ion_species_selector(impurity_nucleons, impurity_charge)
                result[species_name] = Species(
                    species_type=species_name,
                    charge=UnitSpline(ne_psi_n, impurity_charge * unit_charge_array),
                    mass=impurity_mass,
                    dens=impurity_dens_func,
                    temp=ion_temp_func,
                    omega0=omega_func,
                    rho=rho_func,
                )

        if fast_particle == 1:  # Adding the fast particle species.
            nb_psi_n = profiles["nb"]["psinorm"] * units.dimensionless
            fast_ion_dens_data = profiles["nb"]["data"] * 1e20 * units.meter**-3

            pb_psi_n = profiles["pb"]["psinorm"] * units.dimensionless
            fast_ion_press_data = profiles["pb"]["data"] * 1e3 * units.pascals

            if np.all(pb_psi_n != nb_psi_n):
                fast_ion_press_func = UnitSpline(pb_psi_n, fast_ion_press_data)
                fast_ion_press_data = fast_ion_press_func(nb_psi_n)

            fast_ion_temp_data = np_to_T(fast_ion_dens_data, fast_ion_press_data)

            fast_ion_dens_func = UnitSpline(nb_psi_n, fast_ion_dens_data)
            fast_ion_temp_func = UnitSpline(nb_psi_n, fast_ion_temp_data)

            fast_ion_charge = species[-1]["Z"] * units.elementary_charge
            fast_ion_nucleons = species[-1]["A"]
            fast_ion_mass = fast_ion_nucleons * deuterium_mass / 2.0

            fast_species = ion_species_selector(
                fast_ion_nucleons, fast_ion_charge
            ) + str("_fast")

            result[fast_species] = Species(
                species_type=fast_species,
                charge=UnitSpline(ne_psi_n, fast_ion_charge * unit_charge_array),
                mass=fast_ion_mass,
                dens=fast_ion_dens_func,
                temp=fast_ion_temp_func,
                omega0=omega_func,
                rho=rho_func,
            )

        return Kinetics(kinetics_type="pFile", **result)

    def verify_file_type(self, filename: PathLike) -> None:
        """Quickly verify that we're looking at a pFile file without processing"""
        # Check that the header line looks like a pFile header
        with open(filename) as f:
            header = f.readline().split()
        if not re.match(r"\d*", header[0]):
            raise ValueError("pFile header should start with an int")
        if not header[1] == "psinorm":
            raise ValueError("pFile first column name should be 'psinorm'")
