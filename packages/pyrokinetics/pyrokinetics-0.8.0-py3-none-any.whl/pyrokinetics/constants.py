import numpy as np
from scipy import constants

from .units import ureg as units

bk = constants.k
pi = constants.pi
mu0 = constants.mu_0
eps0 = constants.epsilon_0

electron_charge = constants.elementary_charge * units.elementary_charge

electron_mass = constants.electron_mass * units.kg
hydrogen_mass = constants.proton_mass * units.kg
deuterium_mass = constants.physical_constants["deuteron mass"][0] * units.kg
tritium_mass = constants.physical_constants["triton mass"][0] * units.kg

sqrt2 = np.sqrt(2)
