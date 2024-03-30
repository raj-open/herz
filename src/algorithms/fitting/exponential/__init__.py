#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# Exponential fitting of curves #

Given is a monoton data series `P` vs. `V`.

The goal of this submodule is to fit following model:
```
P(V) = A + B·exp(β·V)
```
with parameters `A`, `B`, `β`.

## Heuristic computation for initial conditions ##

Consider two arbitrary points on the curve:
`(V₁, P₁)`, `(V₂, P₂)`.
We assume:
```
V₁ < V₂
P₁ < P₂
```

Set
```
κ := log(1 + 2∆P/P₁)
β := κ/∆V
```

Then
```
e^{κ} - 1 = 2∆P/P₁
βV₂ = β∆V + βV₁ = κ + βV₁
P₂ - P₁·e^{κ}
    = ∆P + P₁·(1 - e^{κ})
    = ∆P - P₁·(e^{κ} - 1)
    = ∆P - P₁·(2∆P/P₁)
    = -∆P
```

Consider
```
A := ½P₁
B := ½P₁·e^{-βV₁}
```

Then the function
```
P(V) := A + B·exp(β·V)
```
satisfies
```
P(V₁) = A + B·e^{βV₁}
    = ½P₁ + ½P₁
    = P₁
P(V₂) = A + ½P₁·e^{β∆V}
    = A + ½P₁·e^{κ}
    = A + ½P₁·(1 + 2∆P/P₁)
    = P₂
```

Hence the choice of `A`, `B`, `β`
here suffices to fit the two points.

# Bounds #

If `(V₁, P₁)` and `(V₂, P₂)` are distinct but "very close",
the by the above a model which fits the points is
```
P(V) = ½P₁·(1 + e^{β·(V - V₁)})
```
where
```
β = log(1 + 2∆P/P₁)/∆V
    ≈ (2∆P/P₁)/∆V
    ≈ 2·(dP/dV)/P₁
```

This provides us with the means to provide bounds on the range of β-values:
```
β_min := min 2·(P´/P) / V´
β_max := max 2·(P´/P) / V´
```
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from .fit import *
from .options import *
from .conditions import *
from .parameters import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'fit_exponential_curve',
    'fit_options_gradients_data',
    'fit_options_scale_data',
    'get_bounds_from_settings',
    'get_initialisation_from_settings',
    'get_schema_from_settings',
]
