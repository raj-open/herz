#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from matplotlib import pyplot as mplot
from matplotlib import colors as mcolours
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch

# NOTE: reference https://plotly.com/python/reference
import plotly
from plotly.subplots import make_subplots
import plotly.express as pex
import plotly.graph_objects as pgo

from enum import Enum

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


class PLOTLY_COLOUR_SCHEME(Enum):
    '''
    Colour schemes for Plotly <https://plotly.com/python/builtin-colorscales>
    '''

    AGGRNYL = 'aggrnyl'
    AGSUNSET = 'agsunset'
    ALGAE = 'algae'
    AMP = 'amp'
    ARMYROSE = 'armyrose'
    BALANCE = 'balance'
    BLACKBODY = 'blackbody'
    BLUERED = 'bluered'
    BLUES = 'blues'
    BLUGRN = 'blugrn'
    BLUYL = 'bluyl'
    BRBG = 'brbg'
    BRWNYL = 'brwnyl'
    BUGN = 'bugn'
    BUPU = 'bupu'
    BURG = 'burg'
    BURGYL = 'burgyl'
    CIVIDIS = 'cividis'
    CURL = 'curl'
    DARKMINT = 'darkmint'
    DEEP = 'deep'
    DELTA = 'delta'
    DENSE = 'dense'
    EARTH = 'earth'
    EDGE = 'edge'
    ELECTRIC = 'electric'
    EMRLD = 'emrld'
    FALL = 'fall'
    GEYSER = 'geyser'
    GNBU = 'gnbu'
    GRAY = 'gray'
    GREENS = 'greens'
    GREYS = 'greys'
    HALINE = 'haline'
    HOT = 'hot'
    HSV = 'hsv'
    ICE = 'ice'
    ICEFIRE = 'icefire'
    INFERNO = 'inferno'
    JET = 'jet'
    MAGENTA = 'magenta'
    MAGMA = 'magma'
    MATTER = 'matter'
    MINT = 'mint'
    MRYBM = 'mrybm'
    MYGBM = 'mygbm'
    ORANGES = 'oranges'
    ORRD = 'orrd'
    ORYEL = 'oryel'
    OXY = 'oxy'
    PEACH = 'peach'
    PHASE = 'phase'
    PICNIC = 'picnic'
    PINKYL = 'pinkyl'
    PIYG = 'piyg'
    PLASMA = 'plasma'
    PLOTLY3 = 'plotly3'
    PORTLAND = 'portland'
    PRGN = 'prgn'
    PUBU = 'pubu'
    PUBUGN = 'pubugn'
    PUOR = 'puor'
    PURD = 'purd'
    PURP = 'purp'
    PURPLES = 'purples'
    PURPOR = 'purpor'
    RAINBOW = 'rainbow'
    RDBU = 'rdbu'
    RDGY = 'rdgy'
    RDPU = 'rdpu'
    RDYLBU = 'rdylbu'
    RDYLGN = 'rdylgn'
    REDOR = 'redor'
    REDS = 'reds'
    SOLAR = 'solar'
    SPECTRAL = 'spectral'
    SPEED = 'speed'
    SUNSET = 'sunset'
    SUNSETDARK = 'sunsetdark'
    TEAL = 'teal'
    TEALGRN = 'tealgrn'
    TEALROSE = 'tealrose'
    TEMPO = 'tempo'
    TEMPS = 'temps'
    THERMAL = 'thermal'
    TROPIC = 'tropic'
    TURBID = 'turbid'
    TURBO = 'turbo'
    TWILIGHT = 'twilight'
    VIRIDIS = 'viridis'
    YLGN = 'ylgn'
    YLGNBU = 'ylgnbu'
    YLORBR = 'ylorbr'
    YLORRD = 'ylorrd'


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'Axes',
    'FancyArrowPatch',
    'Figure',
    'PLOTLY_COLOUR_SCHEME',
    'make_subplots',
    'mcolours',
    'mplot',
    'pgo',
    'plotly',
    'pex',
]
