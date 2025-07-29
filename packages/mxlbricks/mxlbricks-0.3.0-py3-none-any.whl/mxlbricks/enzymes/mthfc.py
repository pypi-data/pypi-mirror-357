"""Methenyltetrahydrofolate cyclohydrolase

EC 3.5.4.9
Metacyc: MTHFC

10-FORMYL-THF_m + 0.07 PROTON_m <=> 5-10-METHENYL-THF_m + WATER_m

Equilibrator
10-Formyl-THF(aq) ⇌ 5,10-Methenyltetrahydrofolate(aq) + H2O(l)
Keq = 0.1 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mxlbricks import names as n
from mxlbricks.fns import (
    mass_action_1s,
    reversible_michaelis_menten_1s_1p,
)
from mxlbricks.utils import filter_stoichiometry, static

if TYPE_CHECKING:
    from mxlpy import Model

ENZYME = n.mthfc()


def add_mthfc(
    model: Model,
    mit: str,
    *,
    kcat: str | None = None,
    e0: str | None = None,
    kms: str | None = None,
    kmp: str | None = None,
    keq: str | None = None,
) -> Model:
    kms = static(model, n.kms(ENZYME), 0.2) if kms is None else kms  # FIXME: source
    kmp = static(model, n.kmp(ENZYME), 0.04) if kmp is None else kmp  # FIXME: source
    kcat = (
        static(model, n.kcat(ENZYME), 40.0) if kcat is None else kcat
    )  # FIXME: source
    e0 = static(model, n.e0(ENZYME), 1.0) if e0 is None else e0  # FIXME: source
    keq = static(model, n.keq(ENZYME), 0.1) if keq is None else keq  # FIXME: source
    model.add_derived(vmax := n.vmax(ENZYME), fn=mass_action_1s, args=[kcat, e0])

    model.add_reaction(
        name=ENZYME,
        fn=reversible_michaelis_menten_1s_1p,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.formyl_thf(mit): -1,
                n.methenyl_thf(mit): 1,
            },
        ),
        args=[
            n.formyl_thf(mit),
            n.methenyl_thf(mit),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )

    return model
