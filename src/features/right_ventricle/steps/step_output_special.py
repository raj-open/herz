#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import csv
import math
from math import pi

import pandas as pd
from tabulate import tabulate

from ....core.log import *
from ....models.fitting import *
from ....models.intervals import *
from ....models.polynomials import *
from ....models.user import *
from ....queries.fitting import *
from ....queries.scientific import *
from ....setup import config
from ....thirdparty.maths import *
from ....thirdparty.misc import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "step_output_special_points",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message="STEP output table of special points", level=LOG_LEVELS.INFO)
def step_output_special_points(
    case: RequestConfig,
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    interpols_trig_p: tuple[
        FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]
    ],
    interpols_trig_v: tuple[
        FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]
    ],
    cfg_trig_p: InterpConfigTrig | None,
    cfg_trig_v: InterpConfigTrig | None,
    fitinfo_exp: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
):
    path = case.output.table.path.root
    path = path.format(label=case.label, kind="special")
    T_p = info_p.period
    T_v = info_v.period

    # place special points in table
    units = output_units(case.output.quantities)
    cv = output_conversions(case.output.quantities, units=config.UNITS)
    data = []

    data.append(
        {"name": case.name, "description": f"Results of {case.feature.value} computations."}
    )

    for quantity, T, special in [
        ("pressure", T_p, special_p),
        ("volume", T_v, special_v),
    ]:
        data.append({})
        data.append(
            {
                "name": f"{quantity.upper()}",
                "description": f"Special points for {quantity} curve",
            }
        )
        points = sorted(special.items(), key=lambda x: x[1].time)
        for key, point in points:
            if key == "align" and point.found:
                continue
            data.append(
                {
                    "name": point.name_simple or point.name,
                    "description": point.description,
                    "time": cv["time"] * point.time,
                    "unit-t": units["time"],
                    "value": cv[quantity] * point.value,
                    "unit-x": units[quantity],
                }
            )
        data.append(
            {"name": "Period", "time": cv["time"] * T, "unit-t": units["time"]},
        )

    for quantity, symb, T, interpols_trig, cfg_trig, special in [
        ("pressure", "P", T_p, interpols_trig_p, cfg_trig_p, special_p),
        ("volume", "V", T_v, interpols_trig_v, cfg_trig_v, special_v),
    ]:
        fit, _, intervals = interpols_trig
        if fit is None:
            continue

        intervals = collapse_intervals_to_cycle(intervals, offset=0, period=T)
        intervals_expr = [
            f"t: {cv['time'] * a:.2f}–{cv['time'] * b:.2f} {units['time']}"
            for a, b in intervals
        ]
        omega = 2 * pi / fit.hscale

        if cfg_trig.solver.drift:
            model = "A·cos(ω·(t - t₀)) + C + μ·t"
        else:
            model = "A·cos(ω·(t - t₀)) + C"

        data.append({})
        data += [
            {
                "name": "TRIGONOMETRIC FIT",
                "description": dedent(
                    f"""
                    L²-fitted model
                    {symb}(t) ≈ {model}
                    for parts of {symb}-curve in range
                    {{ranges}}.
                    """
                ).format(ranges=";\n".join(intervals_expr)),
            },
            {
                "name": "A",
                "value": cv[quantity] * fit.vscale,
                "unit-x": units[quantity],
            },
            {
                "name": "ω",
                "value": cv["frequency"] * omega,
                "unit-x": units["frequency"],
            },
            {
                "name": "t₀",
                "value": cv["time"] * (fit.hshift % T),
                "unit-x": units["time"],
            },
            {
                "name": "C",
                "value": cv[quantity] * fit.vshift,
                "unit-x": units[quantity],
            },
        ]
        if cfg_trig.solver.drift:
            data.append(
                {
                    "name": "μ",
                    "value": cv[f"d[1,t]{quantity}"] * fit.drift,
                    "unit-x": units[f"d[1,t]{quantity}"],
                }
            )

    fit_exp, (vmin, vmax), (pmin, pmax) = fitinfo_exp
    beta = 1 / fit_exp.hscale
    alpha = fit_exp.vscale
    alpha0 = alpha * math.exp(beta * vmin)

    data.append({})
    data += [
        {
            "name": "EXPONENTIAL FIT",
            "description": dedent(
                f"""
                L²-fitted model
                P(V) ≈ α·exp(β·V) + C
                or
                P(V) ≈ α₀·exp(β·(V - V₀)) + C
                for parts of P-V-curve in range
                V: V₀={cv["volume"] * vmin:.4g}–{cv["volume"] * vmax:.4g} {units["volume"]};
                P: {cv["pressure"] * pmin:.4g}–{cv["pressure"] * pmax:.4g} {units["pressure"]}.
                """
            ),
        },
        # {
        #     'name': 'α',
        #     'value': cv['pressure'] * fit_exp.vscale,
        #     'unit-x': units['pressure'],
        # },
        {
            "name": "α₀",
            "value": cv["pressure"] * alpha0,
            "unit-x": units["pressure"],
        },
        {
            "name": "β",
            "value": beta / cv["volume"],
            "unit-x": f"1/{units['volume']}",
        },
        {
            "name": "C",
            "value": cv["pressure"] * fit_exp.vshift,
            "unit-x": units["pressure"],
        },
    ]

    data.append({})
    data.append({"name": "P-V", "description": "Parameters computed for P-V curve"})
    for _, point in special_pv.items():
        if not point.found:
            continue
        match point.kind:
            case EnumSpecialPointPVKind.PRESSURE:
                quantity = "pressure"
            case EnumSpecialPointPVKind.VOLUME:
                quantity = "volume"
            case EnumSpecialPointPVKind.GRADIENT:
                quantity = "pressure/volume"
            case _:
                continue
        data.append(
            {
                "name": point.name_simple or point.name,
                "description": point.description,
                "value": cv[quantity] * point.value,
                "unit-x": units[quantity],
            }
        )

    # log to console
    log_debug_wrapped(
        lambda: tabulate(
            data,
            headers={
                "name": "Item",
                "description": "Description",
                "time": "Time",
                "unit-t": "Unit",
                "value": "Quantity",
                "unit-x": "Unit",
            },
            colalign=["left", "left", "right", "left", "right", "left"],
            floatfmt=".4g",
            tablefmt="rst",
        )
    )

    # store as table
    table = pd.DataFrame(data).astype(
        {
            "name": "string",
            "description": "string",
            "time": "float",
            "unit-t": "string",
            "value": "float",
            "unit-x": "string",
        }
    )

    table.to_csv(
        path,
        sep=case.output.table.sep,
        decimal=case.output.table.decimal,
        na_rep="",
        header=["Item", "Description", "Time", "Unit", "Quantity", "Unit"],
        index=False,
        mode="w",
        encoding="utf-8",
        quotechar='"',
        doublequote=True,
        # NOTE: cannot use this together with quoting - otherwise numbers are treated as strings
        # float_format=lambda x: f'{x:.6g}',
        quoting=csv.QUOTE_STRINGS,
    )
    pass
