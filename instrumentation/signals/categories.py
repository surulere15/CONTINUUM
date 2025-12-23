"""
Signal Categories

Definition of the five civilization signal categories.
Each category observes a domain — no interpretation, no scoring.

INSTRUMENTATION MODULE - Phase C. Awareness without influence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Literal
from enum import Enum


class SignalCategory(Enum):
    """The five signal categories."""
    DEMOGRAPHIC = "demographic"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"
    TECHNOLOGICAL = "technological"
    SOCIETAL = "societal"


@dataclass(frozen=True)
class CategoryDefinition:
    """
    Definition of a signal category.
    
    Categories are observational domains — they define
    what can be observed, not what should be done.
    """
    category: SignalCategory
    description: str
    example_signals: Tuple[str, ...]
    update_frequency: str
    irreversibility_relevance: str


# Category Definitions
DEMOGRAPHIC = CategoryDefinition(
    category=SignalCategory.DEMOGRAPHIC,
    description="Population-level signals about human existence and distribution",
    example_signals=(
        "global_population",
        "birth_rate",
        "mortality_rate",
        "migration_flow",
        "age_distribution",
    ),
    update_frequency="monthly",
    irreversibility_relevance="Direct indicator for O1 (Human Continuity)",
)

ECONOMIC = CategoryDefinition(
    category=SignalCategory.ECONOMIC,
    description="Economic system signals about production, exchange, and resources",
    example_signals=(
        "gdp_growth",
        "unemployment_rate",
        "inflation_rate",
        "trade_volume",
        "resource_prices",
    ),
    update_frequency="daily",
    irreversibility_relevance="Indicator for O2 (Civilizational Stability)",
)

ENVIRONMENTAL = CategoryDefinition(
    category=SignalCategory.ENVIRONMENTAL,
    description="Environmental signals about planetary systems and resources",
    example_signals=(
        "global_temperature",
        "co2_concentration",
        "biodiversity_index",
        "sea_level",
        "forest_coverage",
    ),
    update_frequency="daily",
    irreversibility_relevance="Critical for O1 and O2 (existential risks)",
)

TECHNOLOGICAL = CategoryDefinition(
    category=SignalCategory.TECHNOLOGICAL,
    description="Technology signals about capabilities and infrastructure",
    example_signals=(
        "ai_capability_index",
        "energy_production",
        "internet_coverage",
        "research_output",
        "infrastructure_health",
    ),
    update_frequency="weekly",
    irreversibility_relevance="Relevant for O5 (Adaptive Capacity)",
)

SOCIETAL = CategoryDefinition(
    category=SignalCategory.SOCIETAL,
    description="Social signals about human organization and wellbeing",
    example_signals=(
        "education_access",
        "healthcare_access",
        "social_cohesion",
        "governance_stability",
        "freedom_index",
    ),
    update_frequency="monthly",
    irreversibility_relevance="Relevant for O4 (Human Agency)",
)


# All category definitions
CATEGORY_DEFINITIONS = {
    SignalCategory.DEMOGRAPHIC: DEMOGRAPHIC,
    SignalCategory.ECONOMIC: ECONOMIC,
    SignalCategory.ENVIRONMENTAL: ENVIRONMENTAL,
    SignalCategory.TECHNOLOGICAL: TECHNOLOGICAL,
    SignalCategory.SOCIETAL: SOCIETAL,
}


def get_category(category: SignalCategory) -> CategoryDefinition:
    """Get category definition."""
    return CATEGORY_DEFINITIONS[category]


def list_categories() -> Tuple[SignalCategory, ...]:
    """List all signal categories."""
    return tuple(SignalCategory)
