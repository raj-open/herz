#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.render import *

from ....setup import config
from ....core.log import *
from ....models.fitting import *
from ....models.user import *
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
    fit_trig_p: FittedInfoTrig | None,
    fit_trig_v: FittedInfoTrig | None,
    info_p: FittedInfo,
    info_v: FittedInfo,
):
    path = case.output.table.path.root
    path = path.format(label=case.label, kind=f'special')
    t_align_p = special_p['align'].time
    t_align_v = special_v['align'].time
    T_p = info_p.normalisation.period
    T_v = info_v.normalisation.period

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
            (point.time - t_align_p) % T_p,
            point.value,
        )
        for key, point in special_p.items()
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
            (point.time - t_align_v) % T_v,
            point.value,
        )
        for key, point in special_v.items()
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
        t_align = special['align'].time
        vshift = fit.vshift
        vscale = fit.vscale
        hshift = fit.hshift
        hscale = fit.hscale
        drift = fit.drift
        data += [
            {
                'name': f'Trig {quantity.title()}',
                'description': f'L²-fitted model for parts of {symb}-curve:\nA·cos(ω·(t - t₀)) + C + μ·t',
            },
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
                'value': cv['time'] * ((hshift - t_align) % T),
                'unit-x': units['time'],
            },
            {
                'name': 'C',
                'value': cv[quantity] * vshift,
                'unit-x': units[quantity],
            },
            {
                'name': 'μ',
                'value': (cv[quantity] / cv['time']) * drift,
                'unit-x': f"{units[quantity]}/{units['time']}",
            },
        ]

    data.append({'name': 'P-V', 'description': 'Parameters computed for P-V curve'})
    ees = compute_ees(special_p, special_v)
    ea = compute_ea(special_p, special_v)
    data.append(
        {
            'name': 'ees',
            'value': cv['pressure/volume'] * ees,
            'unit-x': units['pressure/volume'],
        }
    )
    data.append(
        {
            'name': 'ea',
            'value': cv['pressure/volume'] * ea,
            'unit-x': units['pressure/volume'],
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


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def compute_ees(
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
) -> float:
    P_isomax = special_p['iso-max'].value
    P_es = special_p['es'].value
    V_ed = special_v['ed'].value
    V_es = special_v['es'].value
    ees = (P_isomax - P_es) / (V_ed - V_es)
    return ees


def compute_ea(
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
) -> float:
    P_es = special_p['es'].value
    V_ed = special_v['ed'].value
    V_es = special_v['es'].value
    ea = P_es / (V_ed - V_es)
    return ea


def unnormalise(
    key: str,
    special: SpecialPointsConfig,
    info: FittedInfo,
) -> tuple[float, float]:
    point = special[key]
    return get_unnormalised_point(point.time, point.value, info=info)
