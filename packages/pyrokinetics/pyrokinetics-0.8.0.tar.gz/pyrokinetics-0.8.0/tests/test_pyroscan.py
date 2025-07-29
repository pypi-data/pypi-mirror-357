from pyrokinetics.pyroscan import PyroScan
from pyrokinetics import Pyro
from pyrokinetics.units import ureg as units

from pathlib import Path
import numpy as np

import sys

docs_dir = Path(__file__).parent.parent / "docs"
sys.path.append(str(docs_dir))
from examples import example_SCENE  # noqa


def assert_close_or_equal(attr, left_pyroscan, right_pyroscan):
    left = getattr(left_pyroscan, attr)
    right = getattr(right_pyroscan, attr)

    if attr == "parameter_dict":
        assert left.keys() == right.keys()
        for left_value, right_value in zip(left.values(), right.values()):
            assert np.allclose(left_value, right_value)
    elif attr == "pyroscan_json":
        for json_key in left.keys():
            if json_key == "parameter_dict":
                assert left[json_key].keys() == right[json_key].keys()
                for left_value, right_value in zip(
                    left[json_key].values(), right[json_key].values()
                ):
                    assert np.allclose(left_value, right_value)
            else:
                assert json_key in right.keys()
                if isinstance(left[json_key], (str, list, type(None), dict, Path)):
                    assert np.all(left[json_key] == right[json_key])
                else:
                    assert np.allclose(
                        left[json_key], right[json_key]
                    ), f"{left} != {right}"
    else:
        if isinstance(left, (str, list, type(None), dict, Path)):
            assert np.all(left == right)
        else:
            assert np.allclose(left, right), f"{left} != {right}"


def test_compare_read_write_pyroscan(tmp_path):
    pyro = example_SCENE.main(tmp_path)

    parameter_dict = {"ky": [0.1, 0.2, 0.3]}

    initial_pyroscan = PyroScan(pyro, parameter_dict=parameter_dict)

    initial_pyroscan.write(file_name="test_pyroscan.input", base_directory=tmp_path)

    pyroscan_json = tmp_path / "pyroscan.json"

    new_pyroscan = PyroScan(pyro, pyroscan_json=pyroscan_json)

    comparison_attrs = [
        "base_directory",
        "file_name",
        "p_prime_type",
        "parameter_dict",
        "parameter_map",
        "parameter_separator",
        "pyroscan_json",
        "run_directories",
        "value_fmt",
        "value_size",
    ]
    for attrs in comparison_attrs:
        assert_close_or_equal(attrs, initial_pyroscan, new_pyroscan)


def test_format_run_name():
    scan = PyroScan(Pyro(gk_code="GS2"), value_separator="|", parameter_separator="@")

    assert scan.format_single_run_name({"ky": 0.1, "nx": 55}) == "ky|0.10@nx|55.00"


def test_format_run_name_units():
    scan = PyroScan(Pyro(gk_code="GS2"), value_separator="|", parameter_separator="@")

    assert (
        scan.format_single_run_name(
            {"ky": 0.1 * units.rhoref_pyro**-1, "nx": 55 * units.dimensionless}
        )
        == "ky|0.10@nx|55.00"
    )


def test_create_single_run():
    scan = PyroScan(
        Pyro(gk_code="GS2"),
        base_directory="some_dir",
        value_separator="|",
        parameter_separator="@",
    )

    run_parameters = {"ky": 0.1, "nx": 55}
    name, new_run = scan.create_single_run(run_parameters)

    assert name == scan.format_single_run_name(run_parameters)
    assert new_run.file_name == "input.in"
    assert new_run.run_directory == Path(f"./some_dir/{name}").absolute()
    assert new_run.run_parameters == run_parameters


def test_apply_func(tmp_path):
    pyro = example_SCENE.main(tmp_path)

    parameter_dict = {"aln": [1.0, 2.0, 3.0]}

    pyro_scan = PyroScan(pyro, parameter_dict=parameter_dict)

    pyro_scan.add_parameter_key("aln", "local_species", ["electron", "inverse_ln"])

    def maintain_quasineutrality(pyro):
        for species in pyro.local_species.names:
            if species != "electron":
                pyro.local_species[species].inverse_ln = (
                    pyro.local_species.electron.inverse_ln
                )

    parameter_kwargs = {}
    pyro_scan.add_parameter_func("aln", maintain_quasineutrality, parameter_kwargs)

    # Add function to pyro
    pyro_scan.write(file_name="test_pyroscan_func.input", base_directory=tmp_path)

    for pyro in pyro_scan.pyro_dict.values():
        for species in pyro.local_species.names:
            assert (
                pyro.local_species.electron.inverse_ln
                == pyro.local_species[species].inverse_ln
            )
