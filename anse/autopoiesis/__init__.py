"""Autopoiesis sub-package: introspector, architect, hotswap, and AlphaEvolve biomimetic evolution."""

from anse.autopoiesis.alphaevolve_biomimetic import (
    AlphaEvolveBiomimeticEngine,
    ArtificialImmuneSystem,
    ASTGeneticOperators,
    DiploidGenome,
    EpigeneticChromatinState,
    MAPElitesIsland,
)
from anse.autopoiesis.autopoietic_agent import ANSEAutopoieticAgent
from anse.autopoiesis.hypervisor import AutopoiesisHypervisor, RCUComponentProxy
from anse.autopoiesis.registry import ComponentRegistry

__all__ = [
    "ANSEAutopoieticAgent",
    "AlphaEvolveBiomimeticEngine",
    "ArtificialImmuneSystem",
    "ASTGeneticOperators",
    "AutopoiesisHypervisor",
    "ComponentRegistry",
    "DiploidGenome",
    "EpigeneticChromatinState",
    "MAPElitesIsland",
    "RCUComponentProxy",
]

