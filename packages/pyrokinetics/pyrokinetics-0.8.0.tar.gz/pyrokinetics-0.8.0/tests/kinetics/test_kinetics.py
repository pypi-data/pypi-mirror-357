from pyrokinetics.equilibrium import read_equilibrium
from pyrokinetics.kinetics import read_kinetics
from pyrokinetics.constants import electron_mass, deuterium_mass, hydrogen_mass
from pyrokinetics import template_dir

import pytest
import numpy as np

tritium_mass = 1.5 * deuterium_mass
carbon_mass = 6 * deuterium_mass


@pytest.fixture
def scene_file():
    return template_dir.joinpath("scene.cdf")


@pytest.fixture
def jetto_file():
    return template_dir.joinpath("jetto.jsp")


@pytest.fixture
def transp_file():
    return template_dir.joinpath("transp.cdf")


@pytest.fixture
def pfile_file():
    return template_dir.joinpath("pfile.txt")


@pytest.fixture
def gacode_file():
    return template_dir.joinpath("input.gacode")


@pytest.fixture
def imas_file():
    return template_dir.joinpath("core_profiles.h5")


@pytest.fixture
def equilibrium():
    eq_file = template_dir / "test.geqdsk"
    return read_equilibrium(eq_file)


def check_species(
    species,
    name,
    charge,
    mass,
    midpoint_density,
    midpoint_density_gradient,
    midpoint_temperature,
    midpoint_temperature_gradient,
    midpoint_angular_velocity,
    midpoint_angular_velocity_gradient,
):
    assert species.species_type == name
    assert species.mass == mass

    assert np.isclose(species.get_charge(0.5).m, charge)
    assert np.isclose(species.get_dens(0.5).m, midpoint_density)
    assert np.isclose(species.get_norm_dens_gradient(0.5).m, midpoint_density_gradient)
    assert np.isclose(species.get_temp(0.5).m, midpoint_temperature)
    assert np.isclose(
        species.get_norm_temp_gradient(0.5).m, midpoint_temperature_gradient
    )
    assert np.isclose(species.get_angular_velocity(0.5).m, midpoint_angular_velocity)
    assert np.isclose(
        species.get_norm_ang_vel_gradient(0.5).m, midpoint_angular_velocity_gradient
    )


@pytest.mark.parametrize("kinetics_type", ["SCENE", None])
def test_read_scene(scene_file, kinetics_type):
    scene = read_kinetics(scene_file, kinetics_type)
    assert scene.kinetics_type == "SCENE"

    assert scene.nspec == 3
    assert np.array_equal(
        sorted(scene.species_names), sorted(["electron", "deuterium", "tritium"])
    )
    check_species(
        scene.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=1.5116787e20,
        midpoint_density_gradient=0.4247526509961558,
        midpoint_temperature=12174.554122236143,
        midpoint_temperature_gradient=2.782385669107711,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        scene.species_data["deuterium"],
        "deuterium",
        1,
        deuterium_mass,
        midpoint_density=7.558393477464637e19,
        midpoint_density_gradient=0.4247526509961558,
        midpoint_temperature=12174.554122236143,
        midpoint_temperature_gradient=2.782385669107711,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        scene.species_data["tritium"],
        "tritium",
        1,
        tritium_mass,
        midpoint_density=7.558393477464637e19,
        midpoint_density_gradient=0.4247526509961558,
        midpoint_temperature=12174.554122236143,
        midpoint_temperature_gradient=2.782385669107711,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )


@pytest.mark.parametrize("kinetics_type", ["IMAS", None])
def test_read_imas(imas_file, kinetics_type, equilibrium):
    imas = read_kinetics(imas_file, kinetics_type, eq=equilibrium)
    assert imas.kinetics_type == "IMAS"

    assert imas.nspec == 5
    assert np.array_equal(
        sorted(imas.species_names),
        sorted(["electron", "deuterium", "carbon", "tungsten", "nickel"]),
    )

    check_species(
        imas.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=1.30324595e19,
        midpoint_density_gradient=0.9976205393237828,
        midpoint_temperature=1155.3048880626693,
        midpoint_temperature_gradient=2.095455413229988,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )

    check_species(
        imas.species_data["deuterium"],
        "deuterium",
        1,
        deuterium_mass,
        midpoint_density=1.1267877863926372e19,
        midpoint_density_gradient=1.034623039315129,
        midpoint_temperature=1155.3048880626693,
        midpoint_temperature_gradient=2.095455413229988,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )

    check_species(
        imas.species_data["carbon"],
        "carbon",
        6,
        carbon_mass,
        midpoint_density=2.784259094632337e17,
        midpoint_density_gradient=0.7265520251672052,
        midpoint_temperature=1155.3048880626693,
        midpoint_temperature_gradient=2.095455413229988,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )


@pytest.mark.parametrize("kinetics_type", ["JETTO", None])
def test_read_jetto(jetto_file, kinetics_type):
    jetto = read_kinetics(jetto_file, kinetics_type)
    assert jetto.kinetics_type == "JETTO"

    assert jetto.nspec == 4
    assert np.array_equal(
        sorted(jetto.species_names),
        sorted(["electron", "deuterium", "deuterium_fast", "impurity1"]),
    )
    check_species(
        jetto.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=3.98442302e19,
        midpoint_density_gradient=0.24934713314306212,
        midpoint_temperature=2048.70870657,
        midpoint_temperature_gradient=1.877960703115299,
        midpoint_angular_velocity=30084.42620196,
        midpoint_angular_velocity_gradient=1.3539597923978433,
    )
    check_species(
        jetto.species_data["deuterium"],
        "deuterium",
        1,
        deuterium_mass,
        midpoint_density=3.36404139e19,
        midpoint_density_gradient=0.15912588033334082,
        midpoint_temperature=1881.28998733,
        midpoint_temperature_gradient=1.2290413714311896,
        midpoint_angular_velocity=30084.42620196,
        midpoint_angular_velocity_gradient=1.3539597923978433,
    )
    check_species(
        jetto.species_data["impurity1"],
        "impurity1",
        5.99947137,
        12 * hydrogen_mass,
        midpoint_density=8.99100966e17,
        midpoint_density_gradient=0.37761249,
        midpoint_temperature=1881.28998733,
        midpoint_temperature_gradient=1.2290413714311896,
        midpoint_angular_velocity=30084.42620196,
        midpoint_angular_velocity_gradient=1.3539597923978433,
    )
    check_species(
        jetto.species_data["deuterium_fast"],
        "deuterium_fast",
        1.0,
        deuterium_mass,
        midpoint_density=8.09686716e17,
        midpoint_density_gradient=3.1423607191445337,
        midpoint_temperature=21305.937104805435,
        midpoint_temperature_gradient=0.4752751206880977,
        midpoint_angular_velocity=30084.42620196,
        midpoint_angular_velocity_gradient=1.3539597923978433,
    )


@pytest.mark.parametrize("kinetics_type", ["TRANSP", None])
def test_read_transp(transp_file, kinetics_type):
    transp = read_kinetics(transp_file, kinetics_type)
    assert transp.kinetics_type == "TRANSP"

    assert transp.nspec == 4
    assert np.array_equal(
        sorted(transp.species_names),
        sorted(["electron", "deuterium", "impurity", "deuterium_fast"]),
    )

    check_species(
        transp.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=3.4654020976732373e19,
        midpoint_density_gradient=0.3026718552809151,
        midpoint_temperature=363.394446992318,
        midpoint_temperature_gradient=2.24450067282526,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        transp.species_data["deuterium"],
        "deuterium",
        1,
        deuterium_mass,
        midpoint_density=3.205339599971588e19,
        midpoint_density_gradient=0.20724602138146409,
        midpoint_temperature=433.128653116985,
        midpoint_temperature_gradient=2.0159650962726197,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        transp.species_data["impurity"],
        "impurity",
        6,
        12 * hydrogen_mass,
        midpoint_density=3.465402009669668e17,
        midpoint_density_gradient=0.30267160173086655,
        midpoint_temperature=432.77471321988463,
        midpoint_temperature_gradient=2.04184150650355,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        transp.species_data["deuterium_fast"],
        "deuterium_fast",
        1,
        1 * deuterium_mass,
        midpoint_density=5.2138297041837216e17,
        midpoint_density_gradient=6.169562307950176,
        midpoint_temperature=16742.28912410173,
        midpoint_temperature_gradient=0.9119287844383214,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )


@pytest.mark.parametrize("kinetics_type", ["TRANSP", None])
def test_read_transp_kwargs(transp_file, kinetics_type):
    transp = read_kinetics(transp_file, kinetics_type, time_index=10)
    assert transp.kinetics_type == "TRANSP"

    assert transp.nspec == 4
    assert np.array_equal(
        sorted(transp.species_names),
        sorted(["electron", "deuterium", "impurity", "deuterium_fast"]),
    )

    check_species(
        transp.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=2.7376385427937518e19,
        midpoint_density_gradient=0.5047111960078463,
        midpoint_temperature=363.2826972873802,
        midpoint_temperature_gradient=3.0269628789570127,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        transp.species_data["deuterium"],
        "deuterium",
        1,
        deuterium_mass,
        midpoint_density=2.546110916694358e19,
        midpoint_density_gradient=0.4352839614277451,
        midpoint_temperature=275.0882425446277,
        midpoint_temperature_gradient=5.312259392804134,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        transp.species_data["impurity"],
        "impurity",
        6,
        12 * hydrogen_mass,
        midpoint_density=2.737639427605868e17,
        midpoint_density_gradient=0.5047206814879348,
        midpoint_temperature=276.32130457101044,
        midpoint_temperature_gradient=5.301042741230228,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )
    check_species(
        transp.species_data["deuterium_fast"],
        "deuterium_fast",
        1,
        1 * deuterium_mass,
        midpoint_density=2.72693515242587e17,
        midpoint_density_gradient=6.9863694819602005,
        midpoint_temperature=26577.97726842,
        midpoint_temperature_gradient=0.5931113899453979,
        midpoint_angular_velocity=0.0,
        midpoint_angular_velocity_gradient=0.0,
    )


@pytest.mark.parametrize("kinetics_type", ["pFile", None])
def test_read_pFile(pfile_file, equilibrium, kinetics_type):
    pfile = read_kinetics(pfile_file, kinetics_type, eq=equilibrium)
    assert pfile.kinetics_type == "pFile"

    assert pfile.nspec == 4
    assert np.array_equal(
        sorted(pfile.species_names),
        sorted(["deuterium", "deuterium_fast", "electron", "impurity"]),
    )
    check_species(
        pfile.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=7.63899297e19,
        midpoint_density_gradient=1.10742399,
        midpoint_temperature=770.37876268,
        midpoint_temperature_gradient=3.1457586490506135,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )
    check_species(
        pfile.species_data["deuterium"],
        "deuterium",
        1,
        deuterium_mass,
        midpoint_density=5.99025662e19,
        midpoint_density_gradient=1.7807398428788435,
        midpoint_temperature=742.54533496,
        midpoint_temperature_gradient=2.410566291534264,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )
    check_species(
        pfile.species_data["impurity"],
        "impurity",
        6,
        6 * deuterium_mass,
        midpoint_density=1.4747197923435095e18,
        midpoint_density_gradient=-3.4544821178030762,
        midpoint_temperature=742.54533496,
        midpoint_temperature_gradient=2.410566291534264,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )
    check_species(
        pfile.species_data["deuterium_fast"],
        "deuterium_fast",
        1,
        deuterium_mass,
        midpoint_density=7.63899297e18,
        midpoint_density_gradient=1.1074239891222437,
        midpoint_temperature=1379.36939199,
        midpoint_temperature_gradient=3.0580150015690317,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )


@pytest.mark.parametrize("kinetics_type", ["GACODE", None])
def test_read_gacode(gacode_file, equilibrium, kinetics_type):
    gacode = read_kinetics(gacode_file, kinetics_type)
    assert gacode.kinetics_type == "GACODE"

    assert gacode.nspec == 4
    assert np.array_equal(
        sorted(gacode.species_names),
        sorted(["deuterium", "deuterium_fast", "electron", "impurity1"]),
    )

    check_species(
        gacode.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=3.90344513e19,
        midpoint_density_gradient=0.24618685944052837,
        midpoint_temperature=2.0487168760575134,
        midpoint_temperature_gradient=2.4720257831420644,
        midpoint_angular_velocity=30084.64386986,
        midpoint_angular_velocity_gradient=1.78730003,
    )
    check_species(
        gacode.species_data["deuterium"],
        "deuterium",
        1,
        deuterium_mass,
        midpoint_density=3.364036907223085e19,
        midpoint_density_gradient=0.20733395590044212,
        midpoint_temperature=1.8812833840152388,
        midpoint_temperature_gradient=1.6103159725032943,
        midpoint_angular_velocity=30084.64386986,
        midpoint_angular_velocity_gradient=1.78730003,
    )
    check_species(
        gacode.species_data["impurity1"],
        "impurity1",
        6,
        6 * deuterium_mass,
        midpoint_density=8.990927564612032e17,
        midpoint_density_gradient=0.48831969476757303,
        midpoint_temperature=1.8812833840152388,
        midpoint_temperature_gradient=1.6103159725032943,
        midpoint_angular_velocity=30084.64386986,
        midpoint_angular_velocity_gradient=1.78730003,
    )
    check_species(
        gacode.species_data["deuterium_fast"],
        "deuterium_fast",
        1,
        deuterium_mass,
        midpoint_density=8.097878630410934e17,
        midpoint_density_gradient=4.272559775542998,
        midpoint_temperature=21.309682394342914,
        midpoint_temperature_gradient=0.6266355862448794,
        midpoint_angular_velocity=30084.64386986,
        midpoint_angular_velocity_gradient=1.78730003,
    )


@pytest.mark.parametrize(
    "filename,kinetics_type",
    [
        ("scene.cdf", "SCENE"),
        ("jetto.jsp", "JETTO"),
        ("transp.cdf", "TRANSP"),
        ("input.gacode", "GACODE"),
    ],
)
def test_filetype_inference(filename, kinetics_type):
    kinetics = read_kinetics(template_dir.joinpath(filename))
    assert kinetics.kinetics_type == kinetics_type


def test_filetype_inference_pfile(pfile_file, equilibrium):
    kinetics = read_kinetics(pfile_file, eq=equilibrium)
    assert kinetics.kinetics_type == "pFile"


def test_bad_kinetics_type(scene_file):
    kinetics = read_kinetics(scene_file)
    with pytest.raises(ValueError):
        kinetics.kinetics_type = "helloworld"


# Compare JETTO and GACODE files with the same Equilibrium
# Compare only the flux surface at ``psi_n=0.5``.
@pytest.fixture(scope="module")
def kin_gacode():
    kin = read_kinetics(template_dir / "input.gacode")
    return kin


@pytest.fixture(scope="module")
def kin_jetto():
    kin = read_kinetics(template_dir / "jetto.jsp", time_index=-1)
    return kin


@pytest.mark.parametrize(
    "attr, unit",
    [
        ("get_charge", "coulomb"),
        ("get_dens", "meter ** -3"),
        ("get_temp", "eV"),
    ],
)
def test_compare_gacode_jetto_attrs(kin_gacode, kin_jetto, attr, unit):
    """
    Compare attributes between equivalent flux surfaces from GACODE and JETTO
    files. Only checks that values are within 5%. Can't compare gradients as
    gacode file uses different equilibrium
    """
    for sp1, sp2 in zip(
        sorted(kin_gacode.species_names), sorted(kin_jetto.species_names)
    ):
        assert np.isclose(
            getattr(kin_gacode.species_data[sp1], attr)(0.5).to(unit).magnitude,
            getattr(kin_jetto.species_data[sp2], attr)(0.5).to(unit).magnitude,
            rtol=5e-2,
        )


@pytest.fixture(scope="module")
def setup_hydrogenic_pfile(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("pfile_hydrogenic")
    with open(template_dir / "pfile.txt", "r") as f:
        lines = f.readlines()
    lines[-2] = " 1.000000   1.000000   1.500000\n"
    print(lines)
    hydrogenic_pfile = tmp_path / "pfile_hydrogenic.txt"
    with open(hydrogenic_pfile, "w") as f:
        f.writelines(lines)

    return hydrogenic_pfile


@pytest.mark.parametrize("kinetics_type", ["pFile", None])
def test_read_pFile_hydrogenic(setup_hydrogenic_pfile, equilibrium, kinetics_type):
    # Rename the ion species in the original pyro object
    hydrogenic_pfile = setup_hydrogenic_pfile

    pfile = read_kinetics(hydrogenic_pfile, kinetics_type, eq=equilibrium)
    assert pfile.kinetics_type == "pFile"

    assert pfile.nspec == 4
    assert np.array_equal(
        sorted(pfile.species_names),
        sorted(["deuterium_fast", "electron", "hydrogenic", "impurity"]),
    )
    check_species(
        pfile.species_data["electron"],
        "electron",
        -1,
        electron_mass,
        midpoint_density=7.63899297e19,
        midpoint_density_gradient=1.10742399,
        midpoint_temperature=770.37876268,
        midpoint_temperature_gradient=3.1457586490506135,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )
    check_species(
        pfile.species_data["hydrogenic"],
        "hydrogenic",
        1,
        deuterium_mass * 0.75,
        midpoint_density=5.99025662e19,
        midpoint_density_gradient=1.7807398428788435,
        midpoint_temperature=742.54533496,
        midpoint_temperature_gradient=2.410566291534264,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )
    check_species(
        pfile.species_data["impurity"],
        "impurity",
        6,
        6 * deuterium_mass,
        midpoint_density=1.4747197923435095e18,
        midpoint_density_gradient=-3.4544821178030762,
        midpoint_temperature=742.54533496,
        midpoint_temperature_gradient=2.410566291534264,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )
    check_species(
        pfile.species_data["deuterium_fast"],
        "deuterium_fast",
        1,
        deuterium_mass,
        midpoint_density=7.63899297e18,
        midpoint_density_gradient=1.1074239891222437,
        midpoint_temperature=1379.36939199,
        midpoint_temperature_gradient=3.0580150015690317,
        midpoint_angular_velocity=16882.124102721187,
        midpoint_angular_velocity_gradient=4.165436791612331,
    )
