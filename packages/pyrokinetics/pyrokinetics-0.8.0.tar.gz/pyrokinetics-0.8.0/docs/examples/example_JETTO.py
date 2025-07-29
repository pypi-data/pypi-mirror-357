from pyrokinetics import Pyro, template_dir
import os
import pathlib
from typing import Union


def main(base_path: Union[os.PathLike, str] = ".", geometry_type: str = "Miller"):
    # Equilibrium file
    eq_file = template_dir / "test.geqdsk"

    # Kinetics data file
    kinetics_file = template_dir / "jetto.jsp"

    # Load up pyro object
    pyro = Pyro(
        eq_file=eq_file,
        kinetics_file=kinetics_file,
        kinetics_type="JETTO",
        kinetics_kwargs={"time": 550},
    )

    # Generate local parameters at psi_n=0.5
    pyro.load_local(psi_n=0.5, local_geometry=geometry_type)

    # Select code as CGYRO
    pyro.gk_code = "CGYRO"

    base_path = pathlib.Path(base_path)

    # Write CGYRO input file using default template
    pyro.write_gk_file(file_name=base_path / "test_jetto.cgyro")

    # Write single GS2 input file, specifying the code type
    # in the call.
    if geometry_type == "Miller":
        pyro.write_gk_file(file_name=base_path / "test_jetto.gs2", gk_code="GS2")

    # Write single GENE input file, specifying the code type
    # in the call.
    pyro.write_gk_file(file_name=base_path / "test_jetto.gene", gk_code="GENE")

    pyro.write_gk_file(file_name=base_path / "test_jetto.tglf", gk_code="TGLF")

    pyro.write_gk_file(file_name=base_path / "test_jetto.gkw", gk_code="GKW")

    if geometry_type == "Miller":
        pyro.write_gk_file(file_name=base_path / "test_jetto.stella", gk_code="STELLA")

    if geometry_type == "Miller":
        pyro.write_gk_file(file_name=base_path / "test_jetto.gx", gk_code="GX")

    return pyro


if __name__ == "__main__":
    main()
