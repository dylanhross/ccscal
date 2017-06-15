"""
globals.py

Global varaibles used in modules throughout the package. DO NOT mess with these unless
you really know what you are doing.

"""

# the factor by which to scale the mass window in text pre-processing
PP_MASS_WIN_SCALE = 2.0

# path to the pre-processing executable
PP_EXE_PATH = "/Users/DylanRoss/Desktop/Projects/ccscal-package/CcsCal/input/PreProcessTxt.exe"

# initial gaussian function sigma parameter
INIT_GAUSS_SIGMA = 10.0

# Savitsky-Golay filter parameters
SG_SMOOTH_WINDOW = 5
SG_SMOOTH_ORDER = 3

# the maximum number of iterations for curve_fit to reach convergence
CURVE_FIT_MAXFEV = 1000

# conversion factor used to convert dt bins to dt in milliseconds
DEFAULT_DTBIN_TO_DT = 0.0689

# default EDC parameter
DEFAULT_EDC = 1.35

# nitrogen mass
N2_MASS = 28.0134

# CCS Calibration power function initial parameters A, t0, and B
INIT_A = 0.0
INIT_T0 = 0.0
INIT_B = 1.0

# height ratios for subplots in calibration curve figure
HEIGHT_RATIO_1 = 5
HEIGHT_RATIO_2 = 2
