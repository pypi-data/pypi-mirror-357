"""name

EC 1.2.3.4

Equilibrator
Oxalate(aq) + O2(aq) + 2 H2O(l) ⇌ Hydrogen peroxide(aq) + 2 CO2(total)
Keq = 2.8e30 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mxlbricks import names as n
from mxlbricks.fns import mass_action_1s, michaelis_menten_2s
from mxlbricks.utils import filter_stoichiometry, static

if TYPE_CHECKING:
    from mxlpy import Model

ENZYME = n.oxalate_oxidase()


def add_oxalate_oxidase(
    model: Model,
    compartment: str = "",
    *,
    kcat: str | None = None,
    e0: str | None = None,
    kms: str | None = None,
) -> Model:
    kms = static(model, n.kms(ENZYME), 0.1) if kms is None else kms  # FIXME: source
    kcat = static(model, n.kcat(ENZYME), 1.0) if kcat is None else kcat  # FIXME: source
    e0 = static(model, n.e0(ENZYME), 1.0) if e0 is None else e0  # FIXME: source
    model.add_derived(vmax := n.vmax(ENZYME), fn=mass_action_1s, args=[kcat, e0])

    model.add_reaction(
        name=ENZYME,
        fn=michaelis_menten_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.oxalate(compartment): -1.0,
                n.o2(compartment): -1.0,
                n.h2o2(compartment): 1.0,
                n.co2(compartment): 2.0,
            },
        ),
        args=[
            n.oxalate(compartment),
            n.o2(compartment),
            vmax,
            kms,
        ],
    )
    return model
