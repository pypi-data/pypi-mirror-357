from pathlib import Path

import h5py
import numpy as np
from periodictable import elements

from ..constants import deuterium_mass, electron_mass
from ..equilibrium import Equilibrium
from ..file_utils import FileReader
from ..species import Species
from ..typing import PathLike
from ..units import UnitSpline
from ..units import ureg as units
from .kinetics import Kinetics


class KineticsReaderIMAS(FileReader, file_type="IMAS", reads=Kinetics):
    r"""
    Class that can read IMAS core_profile h5 files and return ``Kinetics`` objects.
    Users are not recommended to instantiate this class directly, and should instead use
    the functions ``read_kinetics`` or ``Kinetics.read_from_file``. Keyword arguments
    passed to those functions will be forwarded to this class.

    IMAS core_profiles do not contain information about the minor radius, so it is
    necessary to pass an ``Equilibrium` object to ``read_from_file``. This contains
    the mapping from :math:`\psi_\text{N} \rightarrow r/a`.

    See Also
    --------
    Kinetics: Class representing a 1D profiles of species data
    read_kinteics: Read a kinetics file, return an ``Kinetics``.
    """

    def read_from_file(
        self,
        filename: PathLike,
        time_index: int = -1,
        time: float = None,
        eq: Equilibrium = None,
    ) -> Kinetics:
        r"""

        Parameters
        ----------
        filename : Pathlike
            Path to IMAS HDF5 file
        time: Optional[float]
            The time, in seconds, at which kinetics data should be taken. Data will
            be drawn from the time closest to the provided value. Users should only
            provide one of ``time`` or ``time_index``. If neither is provided, data is
            drawn at the last time stamp.
        time_index: Optional[int]
            As an alternative to providing the time directly, users may provide the
            index of the desired time stamp.
        eq: Equilibrium
            ``Equilibrium`` object containing the mapping from :math:`psi_\text{N} \rightarrow r/a`

        Returns
        -------
        Kinetics
        """
        if eq is None:
            raise ValueError(
                f"{self.__class__.__name__} must be provided with an Equilibrium object via"
                "the keyword argument 'eq'. Please load an Equilibrium."
            )

        if time_index is not None and time is not None:
            raise RuntimeError("Cannot set both 'time' and 'time_index'")

        with h5py.File(filename, "r") as raw_file:
            data = raw_file["core_profiles"]

            time_h5 = data["time"][:]
            if time_index is None:
                time_index = -1 if time is None else np.argmin(np.abs(time_h5 - time))

            psi = data["profiles_1d[]&grid&psi"][time_index]
            psi = psi - psi[0]
            psi_n = psi / psi[-1] * units.dimensionless

            unit_charge_array = np.ones(len(psi_n))

            rho = eq.rho(psi_n) * units.lref_minor_radius

            rho_func = UnitSpline(psi_n, rho)

            electron_temp_data = (
                data["profiles_1d[]&electrons&temperature"][time_index, ...] * units.eV
            )
            electron_temp_func = UnitSpline(psi_n, electron_temp_data)

            electron_dens_data = (
                data["profiles_1d[]&electrons&density_thermal"][time_index, ...]
                * units.meter**-3
            )
            electron_dens_func = UnitSpline(psi_n, electron_dens_data)

            if "profiles_1d[]&ion[]&rotation_frequency_tor" in data.keys():
                omega_data = (
                    data["profiles_1d[]&ion[]&rotation_frequency_tor"][
                        time_index,
                        0,
                    ]
                    * units.second**-1
                )
            elif "profiles_1d[]&ion[]&velocity&toroidal" in data.keys():
                Rmaj = eq.R_major(psi_n).m
                omega_data = (
                    data["profiles_1d[]&ion[]&velocity&toroidal"][
                        time_index,
                        0,
                    ]
                    / Rmaj
                    * units.second**-1
                )
            else:
                omega_data = electron_dens_data.m * 0.0 * units.second**-1

            omega_func = UnitSpline(psi_n, omega_data)

            electron_charge = UnitSpline(
                psi_n, -1 * unit_charge_array * units.elementary_charge
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

            # IMAS only has one ion temp

            ion_full_temp_data = (
                data["profiles_1d[]&ion[]&temperature"][time_index, ...] * units.eV
            )

            n_ions = ion_full_temp_data.shape[0]
            unit_array = np.ones(len(psi_n))

            for i_ion in range(n_ions):
                ion_temp_data = ion_full_temp_data[i_ion, :]
                ion_temp_func = UnitSpline(psi_n, ion_temp_data)

                ion_dens_data = (
                    data["profiles_1d[]&ion[]&density"][time_index, i_ion]
                    / units.meter**3
                )
                if np.all(ion_dens_data.m == 0) or np.allclose(ion_dens_data.m, 1.0):
                    continue

                ion_dens_func = UnitSpline(psi_n, ion_dens_data)

                ion_charge_data = data["profiles_1d[]&ion[]&element[]&z_n"][
                    time_index, i_ion, 0
                ]
                ion_charge_func = UnitSpline(
                    psi_n, ion_charge_data * unit_array * units.elementary_charge
                )

                ion_mass = (
                    data["profiles_1d[]&ion[]&element[]&a"][time_index, i_ion, 0]
                    * deuterium_mass
                    / 2
                )
                ion_name = data["profiles_1d[]&ion[]&label"][time_index, i_ion].decode(
                    "utf-8"
                )

                ion_name = ion_name.split("+")[0]
                try:
                    ion_name = getattr(elements, ion_name).name
                except AttributeError:
                    ion_name = ion_name

                result[ion_name] = Species(
                    species_type=ion_name,
                    charge=ion_charge_func,
                    mass=ion_mass,
                    dens=ion_dens_func,
                    temp=ion_temp_func,
                    omega0=omega_func,
                    rho=rho_func,
                )

            # In IMAS file n_ions matches n_ions_fast
            for i_ion in range(n_ions):
                fast_ion_dens_data = (
                    data["profiles_1d[]&ion[]&density_fast"][time_index, i_ion]
                    / units.meter**3
                )
                if np.all(fast_ion_dens_data == 0):
                    continue

                fast_ion_dens_func = UnitSpline(psi_n, fast_ion_dens_data)

                fast_ion_pressure_data = (
                    data["profiles_1d[]&ion[]&pressure_fast_parallel"][
                        time_index, i_ion
                    ]
                    + data["profiles_1d[]&ion[]&pressure_fast_perpendicular"][
                        time_index, i_ion
                    ]
                ) * units.pascals

                fast_ion_temp_data = (fast_ion_pressure_data / fast_ion_dens_data).to(
                    units.eV
                )

                fast_ion_temp_func = UnitSpline(psi_n, fast_ion_temp_data)

                fast_ion_charge_data = data["profiles_1d[]&ion[]&element[]&z_n"][
                    time_index, i_ion, 0
                ]
                fast_ion_charge_func = UnitSpline(
                    psi_n, fast_ion_charge_data * unit_array * units.elementary_charge
                )

                fast_ion_mass = (
                    data["profiles_1d[]&ion[]&element[]&a"][time_index, i_ion, 0]
                    * deuterium_mass
                    / 2
                )
                fast_ion_name = data["profiles_1d[]&ion[]&label"][
                    time_index, i_ion
                ].decode("utf-8")

                fast_ion_name = fast_ion_name.split("+")[0]
                try:
                    fast_ion_name = getattr(elements, fast_ion_name).name + "_fast"
                except AttributeError:
                    fast_ion_name = fast_ion_name + "_fast"

                result[fast_ion_name] = Species(
                    species_type=fast_ion_name,
                    charge=fast_ion_charge_func,
                    mass=fast_ion_mass,
                    dens=fast_ion_dens_func,
                    temp=fast_ion_temp_func,
                    omega0=omega_func,
                    rho=rho_func,
                )

        return Kinetics(kinetics_type="IMAS", **result)

    def verify_file_type(self, filename: PathLike) -> None:
        """Quickly verify that we're looking at a IMAS file without processing"""
        # Try opening data file
        # If it doesn't exist or isn't netcdf, this will fail
        test_keys = ["ids_properties&creation_date", "ids_properties&homogeneous_time"]
        filename = Path(filename)
        if not filename.is_file():
            raise FileNotFoundError(filename)
        try:
            with h5py.File(filename, "r") as f:
                base_keys = list(f.keys())
                if "core_profiles" not in base_keys:
                    raise ValueError(
                        f"KineticsReaderIMAS was provided an invalid HDF5 file which is missing core_profiles data key: {filename}"
                    )
                eq_keys = list(f["core_profiles"])
                if not np.all(np.isin(test_keys, list(eq_keys))):
                    raise ValueError(
                        f"KineticsReaderIMAS was provided an invalid HDF5 file: {filename}"
                    )
        except Exception as exc:
            raise ValueError("Couldn't read IMAS file. Is the format correct?") from exc
