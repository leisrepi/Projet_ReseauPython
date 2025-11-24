"""Structures de données liées au découpage en sous-réseaux.

Ce module isole l'état manipulé par le contrôleur et la vue pour éviter
de mélanger données et logique d'affichage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SubnettingData:
    """Représente l'état d'une découpe réseau en cours de modification."""

    nb_subnets: int = 0
    nb_max_machines_per_subnet: int = 0
    nb_machines_per_subnet: List[int] = field(default_factory=list)
    network: Optional[str] = None
    mask: Optional[str] = None
    subnetting_name: Optional[str] = None

    def ensure_machine_slots(self, nb_subnets: int) -> None:
        """Garantit que la liste du nombre de machines suit le nombre de sous-réseaux."""

        if nb_subnets < len(self.nb_machines_per_subnet):
            self.nb_machines_per_subnet = self.nb_machines_per_subnet[:nb_subnets]
        else:
            self.nb_machines_per_subnet.extend([0] * (nb_subnets - len(self.nb_machines_per_subnet)))

