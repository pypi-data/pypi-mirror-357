from pathlib import Path

import numpy as np
import pytest
import sys

from pyrokinetics import template_dir
from pyrokinetics.gk_code import GKInputTGLF
from pyrokinetics.local_geometry import LocalGeometryMiller
from pyrokinetics.local_species import LocalSpecies
from pyrokinetics.numerics import Numerics

docs_dir = Path(__file__).parent.parent.parent / "docs"
sys.path.append(str(docs_dir))
from examples import example_JETTO  # noqa

template_file = template_dir / "input.tglf"


@pytest.fixture
def default_tglf():
    return GKInputTGLF()


@pytest.fixture
def tglf():
    return GKInputTGLF(template_file)


def test_read(tglf):
    """Ensure a tglf file can be read, and that the 'data' attribute is set"""
    params = ["geometry_flag", "q_loc", "zs_1"]
    assert np.all(np.isin(params, list(tglf.data)))


def test_read_str():
    """Ensure a tglf file can be read as a string, and that the 'data' attribute is set"""
    params = ["geometry_flag", "q_loc", "zs_1"]
    with open(template_file, "r") as f:
        tglf = GKInputTGLF.from_str(f.read())
        assert np.all(np.isin(params, list(tglf.data)))


def test_verify_file_type(tglf):
    """Ensure that 'verify_file_type' does not raise exception on TGLF file"""
    tglf.verify_file_type(template_file)


@pytest.mark.parametrize(
    "filename", ["input.cgyro", "input.gene", "transp.cdf", "helloworld"]
)
def test_verify_bad_inputs(tglf, filename):
    """Ensure that 'verify' raises exception on non-TGLF file"""
    with pytest.raises(Exception):
        tglf.verify_file_type(template_dir / filename)


def test_is_nonlinear(tglf):
    """Expect template file to be linear. Modify it so that it is nonlinear."""
    tglf.data["use_transport_model"] = False
    assert tglf.is_linear()
    assert not tglf.is_nonlinear()
    tglf.data["use_transport_model"] = True
    assert not tglf.is_linear()
    assert tglf.is_nonlinear()


def test_add_flags(tglf):
    tglf.add_flags({"foo": "bar"})
    assert tglf.data["foo"] == "bar"


def test_get_local_geometry(tglf):
    # TODO test it has the correct values
    local_geometry = tglf.get_local_geometry()
    assert isinstance(local_geometry, LocalGeometryMiller)


def test_get_local_species(tglf):
    local_species = tglf.get_local_species()
    assert isinstance(local_species, LocalSpecies)
    assert local_species.nspec == 2
    # TODO test it has the correct values
    assert local_species["electron"]
    assert local_species["ion1"]


def test_get_numerics(tglf):
    # TODO test it has the correct values
    numerics = tglf.get_numerics()
    assert isinstance(numerics, Numerics)


def test_write(tmp_path, tglf):
    """Ensure a tglf file can be written, and that no info is lost in the process"""
    # Get template data
    local_geometry = tglf.get_local_geometry()
    local_species = tglf.get_local_species()
    numerics = tglf.get_numerics()
    # Set output path
    filename = tmp_path / "input.in"
    # Write out a new input file
    tglf_writer = GKInputTGLF()
    tglf_writer.set(local_geometry, local_species, numerics)
    tglf_writer.write(filename)
    # Ensure a new file exists
    assert Path(filename).exists()
    # Ensure it is a valid file
    GKInputTGLF().verify_file_type(filename)
    tglf_reader = GKInputTGLF(filename)
    new_local_geometry = tglf_reader.get_local_geometry()
    assert local_geometry.shat == new_local_geometry.shat
    new_local_species = tglf_reader.get_local_species()
    assert local_species.nspec == new_local_species.nspec
    new_numerics = tglf_reader.get_numerics()
    assert numerics.ky == new_numerics.ky


def test_drop_species(tmp_path):
    pyro = example_JETTO.main(tmp_path)
    pyro.gk_code = "TGLF"

    n_species = pyro.local_species.nspec
    stored_species = len([key for key in pyro.gk_input.data.keys() if "zs_" in key])
    assert stored_species == n_species

    pyro.local_species.merge_species(
        base_species="deuterium",
        merge_species=["deuterium", "impurity1"],
        keep_base_species_z=True,
        keep_base_species_mass=True,
    )

    pyro.update_gk_code()
    n_species = pyro.local_species.nspec
    stored_species = len([key for key in pyro.gk_input.data.keys() if "zs_" in key])
    assert stored_species == n_species
