from pathlib import Path

import numpy as np
import pytest
import sys

from pyrokinetics import Pyro, template_dir
from pyrokinetics.gk_code import GKInputCGYRO
from pyrokinetics.local_geometry import LocalGeometryMiller
from pyrokinetics.local_species import LocalSpecies
from pyrokinetics.numerics import Numerics

docs_dir = Path(__file__).parent.parent.parent / "docs"
sys.path.append(str(docs_dir))
from examples import example_JETTO  # noqa

template_file = template_dir / "input.cgyro"


@pytest.fixture
def default_cgyro():
    return GKInputCGYRO()


@pytest.fixture
def cgyro():
    return GKInputCGYRO(template_file)


def test_read(cgyro):
    """Ensure a cgyro file can be read, and that the 'data' attribute is set"""
    params = ["EQUILIBRIUM_MODEL", "S", "MAX_TIME"]
    assert np.all(np.isin(params, list(cgyro.data)))


def test_read_str():
    """Ensure a cgyro file can be read as a string, and that the 'data' attribute is set"""
    params = ["EQUILIBRIUM_MODEL", "S", "MAX_TIME"]
    with open(template_file, "r") as f:
        cgyro = GKInputCGYRO.from_str(f.read())
        assert np.all(np.isin(params, list(cgyro.data)))


def test_verify_file_type(cgyro):
    """Ensure that 'verify_file_type' does not raise exception on CGYRO file"""
    cgyro.verify_file_type(template_file)


@pytest.mark.parametrize(
    "filename", ["input.gs2", "input.gene", "transp.cdf", "helloworld"]
)
def test_verify_file_type_bad_inputs(cgyro, filename):
    """Ensure that 'verify_file_type' raises exception on non-CGYRO file"""
    with pytest.raises(Exception):
        cgyro.verify_file_type(template_dir / filename)


def test_is_nonlinear(cgyro):
    """Expect template file to be linear. Modify it so that it is nonlinear."""
    cgyro.data["NONLINEAR_FLAG"] = 0
    assert cgyro.is_linear()
    assert not cgyro.is_nonlinear()
    cgyro.data["NONLINEAR_FLAG"] = 1
    assert not cgyro.is_linear()
    assert cgyro.is_nonlinear()


def test_add_flags(cgyro):
    cgyro.add_flags({"foo": "bar"})
    assert cgyro.data["foo"] == "bar"


def test_get_local_geometry(cgyro):
    # TODO test it has the correct values
    local_geometry = cgyro.get_local_geometry()
    assert isinstance(local_geometry, LocalGeometryMiller)


def test_get_local_species(cgyro):
    local_species = cgyro.get_local_species()
    assert isinstance(local_species, LocalSpecies)
    assert local_species.nspec == 2
    # TODO test it has the correct values
    assert local_species["electron"]
    assert local_species["ion1"]


def test_get_numerics(cgyro):
    # TODO test it has the correct values
    numerics = cgyro.get_numerics()
    assert isinstance(numerics, Numerics)


def test_write(tmp_path, cgyro):
    """Ensure a cgyro file can be written, and that no info is lost in the process"""
    # Get template data
    local_geometry = cgyro.get_local_geometry()
    local_species = cgyro.get_local_species()
    numerics = cgyro.get_numerics()
    # Set output path
    filename = tmp_path / "input.in"
    # Write out a new input file
    cgyro_writer = GKInputCGYRO()
    cgyro_writer.set(local_geometry, local_species, numerics)
    cgyro_writer.write(filename)
    # Ensure a new file exists
    assert Path(filename).exists()
    # Ensure it is a valid file
    GKInputCGYRO().verify_file_type(filename)
    cgyro_reader = GKInputCGYRO(filename)
    new_local_geometry = cgyro_reader.get_local_geometry()
    assert local_geometry.shat == new_local_geometry.shat
    new_local_species = cgyro_reader.get_local_species()
    assert local_species.nspec == new_local_species.nspec
    new_numerics = cgyro_reader.get_numerics()
    assert numerics.delta_time == new_numerics.delta_time


def test_beta_star_scale(tmp_path):
    pyro = Pyro(gk_file=template_dir / "input.gs2")

    pyro.gk_code = "CGYRO"

    pyro.write_gk_file(tmp_path / "input.cgyro")

    assert pyro.gk_input.data["BETA_STAR_SCALE"] == 1.0


def test_drop_species(tmp_path):
    pyro = example_JETTO.main(tmp_path)
    pyro.gk_code = "CGYRO"

    n_species = pyro.local_species.nspec
    stored_species = len([key for key in pyro.gk_input.data.keys() if "DENS_" in key])
    assert stored_species == n_species

    pyro.local_species.merge_species(
        base_species="deuterium",
        merge_species=["deuterium", "impurity1"],
        keep_base_species_z=True,
        keep_base_species_mass=True,
    )

    pyro.update_gk_code()
    n_species = pyro.local_species.nspec
    stored_species = len([key for key in pyro.gk_input.data.keys() if "DENS_" in key])
    assert stored_species == n_species
