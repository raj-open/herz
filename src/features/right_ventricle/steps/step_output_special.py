#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.misc import *
from ....thirdparty.render import *

from ....setup import config
from ....core.log import *
from ....models.fitting import *
from ....models.user import *
from ....models.polynomials import *
from ....queries.fitting import *
from ....queries.scientific import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_output_special_points',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP output table of special points', level=LOG_LEVELS.INFO)
def step_output_special_points(
    case: RequestConfig,
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
    info_p: FittedInfoNormalisation,
    info_v: FittedInfoNormalisation,
    # fit_poly_p: FittedInfoPoly,
    # fit_poly_v: FittedInfoPoly,
    fit_trig_p: FittedInfoTrig | None,
    fit_trig_v: FittedInfoTrig | None,
    fitinfo_exp: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
):
    path = case.output.table.path.root
    path = path.format(label=case.label, kind=f'special')
    T_p = info_p.period
    T_v = info_v.period

    # place special points in table
    units = output_units(case.output.quantities)
    cv = output_conversions(case.output.quantities, units=config.UNITS)
    data = []

    data.append({'name': 'Pressure', 'description': 'Special points for pressure curve'})
    data.append({'name': 'Period', 'time': cv['time'] * T_p, 'unit-t': units['time']})
    points = [
        (
            key,
            point.name_simple or point.name,
            point.time,
            point.value,
        )
        for key, point in special_p.items()
        if point.found
    ]
    points = sorted(points, key=lambda x: x[2])
    for key, name, t, x in points:
        if key == 'align':
            continue
        data.append(
            {
                'name': name,
                'time': cv['time'] * t,
                'unit-t': units['time'],
                'value': cv['pressure'] * x,
                'unit-x': units['pressure'],
            }
        )

    data.append({'name': 'Volume', 'description': 'Special points for volume curve'})
    data.append({'name': 'Period', 'time': cv['time'] * T_v, 'unit-t': units['time']})
    points = [
        (
            key,
            point.name_simple or point.name,
            point.time,
            point.value,
        )
        for key, point in special_v.items()
        if point.found
    ]
    points = sorted(points, key=lambda x: x[2])
    for key, name, t, x in points:
        if key == 'align':
            continue
        data.append(
            {
                'name': name,
                'time': cv['time'] * t,
                'unit-t': units['time'],
                'value': cv['volume'] * x,
                'unit-x': units['volume'],
            }
        )

    for quantity, symb, T, fit, special in [
        ('pressure', 'P', T_p, fit_trig_p, special_p),
        ('volume', 'V', T_v, fit_trig_v, special_v),
    ]:
        if fit is None:
            continue
        vshift = fit.vshift
        vscale = fit.vscale
        hshift = fit.hshift % T
        hscale = fit.hscale
        drift = fit.drift
        if drift == 0:
            data.append(
                {
                    'name': f'Trig {quantity.title()}',
                    'description': f'L²-fitted model for parts of {symb}-curve:\nA·cos(ω·(t - t₀)) + C',
                }
            )
        else:
            data.append(
                {
                    'name': f'Trig {quantity.title()}',
                    'description': f'L²-fitted model for parts of {symb}-curve:\nA·cos(ω·(t - t₀)) + C + μ·t',
                }
            )
        data += [
            {
                'name': 'A',
                'value': cv[quantity] * vscale,
                'unit-x': units[quantity],
            },
            {
                'name': 'ω',
                'value': cv['frequency'] * (2 * pi / hscale),
                'unit-x': units['frequency'],
            },
            {
                'name': 't₀',
                'value': cv['time'] * hshift,
                'unit-x': units['time'],
            },
            {
                'name': 'C',
                'value': cv[quantity] * vshift,
                'unit-x': units[quantity],
            },
        ]
        if drift != 0:
            data.append(
                {
                    'name': 'μ',
                    'value': cv[f'd[1,t]{quantity}'] * drift,
                    'unit-x': units[f'd[1,t]{quantity}'],
                }
            )

    data.append({'name': ''})
    fit_exp, (vmin, vmax), (pmin, pmax) = fitinfo_exp
    vshift = fit_exp.vshift
    vscale = fit_exp.vscale
    hscale = fit_exp.hscale
    data += [
        {
            'name': f'Exponential Fit',
            'description': dedent(
                f'''
                L²-fitted model
                P(V) ≈ α·exp(β·V) + C
                for parts of P-V-curve in range
                V: {cv['volume'] * vmin:.4g}–{cv['volume'] * vmax:.4g} {units['volume']};
                P: {cv['pressure'] * pmin:.4g}–{cv['pressure'] * pmax:.4g} {units['pressure']}.
                '''
            ),
        },
        {
            'name': 'σ',
            'value': cv['pressure'] * vshift,
            'unit-x': units['pressure'],
        },
        {
            'name': 'β',
            'value': 1 / (cv['volume'] * hscale),
            'unit-x': f"1/{units['volume']}",
        },
        {
            'name': 'C',
            'value': cv['pressure'] * vshift,
            'unit-x': units['pressure'],
        },
    ]

    data.append({'name': 'P-V', 'description': 'Parameters computed for P-V curve'})
    for _, point in special_pv.items():
        if not point.found:
            continue
        match point.kind:
            case EnumSpecialPointPVKind.PRESSURE:
                quantity = 'pressure'
            case EnumSpecialPointPVKind.VOLUME:
                quantity = 'volume'
            case EnumSpecialPointPVKind.GRADIENT:
                quantity = 'pressure/volume'
            case _:
                continue
        data.append(
            {
                'name': point.name_simple or point.name,
                'value': cv[quantity] * point.value,
                'unit-x': units[quantity],
            }
        )

    # log to console
    log_debug_wrapped(
        lambda: tabulate(
            data,
            headers={
                'name': 'Item',
                'description': 'Description',
                'time': f'Time',
                'unit-t': 'Unit',
                'value': 'Quantity',
                'unit-x': 'Unit',
            },
            colalign=['left', 'left', 'right', 'left', 'right', 'left'],
            floatfmt='.4g',
            tablefmt='rst',
        )
    )

    # store as table
    table = pd.DataFrame(data).astype(
        {
            'name': 'string',
            'description': 'string',
            'time': 'float',
            'unit-t': 'string',
            'value': 'float',
            'unit-x': 'string',
        }
    )

    table.to_csv(
        path,
        sep=case.output.table.sep,
        decimal=case.output.table.decimal,
        na_rep='',
        header=['Item', 'Description', 'Time', 'Unit', 'Quantity', 'Unit'],
        index=False,
        mode='w',
        encoding='utf-8',
        quotechar='"',
        doublequote=True,
        float_format=lambda x: f'{x:.6f}',
    )
    pass
