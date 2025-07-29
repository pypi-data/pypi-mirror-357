from pyrokinetics import Pyro, template_dir
import matplotlib.pyplot as plt
import numpy as np

# Point to GS2 input file
gs2_template = template_dir / "outputs/GS2_linear/gs2.in"

# Load in file
pyro = Pyro(gk_file=gs2_template, gk_code="GS2")

# Load in GS2 output data
pyro.load_gk_output()
data = pyro.gk_output

# Get eigenvalues
eigenvalues = data["eigenvalues"]
growth_rate = data["growth_rate"]
mode_freq = data["mode_frequency"]

# Plot growth and mode frequency
growth_rate_tolerance = data["growth_rate_tolerance"]
growth_rate.plot(x="time")
plt.title(f"Growth rate tolerance = {growth_rate_tolerance.data}")
plt.show()

mode_freq.plot(x="time")
plt.show()

# Plot eigenfunction
phi_eig = np.real(data["eigenfunctions"].sel(field="phi").isel(time=-1))
phi_eig.plot(x="theta", label="Real")

phi_i_eig = np.imag(data["eigenfunctions"].sel(field="phi").isel(time=-1))
phi_i_eig.plot(x="theta", label="Imag")

plt.legend()
plt.show()

# Plot electron energy flux
energy_flux = (
    data["heat"].sel(field="phi", species="electron").sum(dim="ky").plot.line()
)
plt.show()

# Plot phi
phi = data["phi"].sel(theta=0.0, method="nearest").isel(ky=0).isel(kx=0)
phi = np.abs(phi)
phi.plot.line(x="time")

plt.yscale("log")
plt.show()
