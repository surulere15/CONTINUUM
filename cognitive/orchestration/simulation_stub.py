"""
Simulation Stub

Prepare for future planning without enabling it.
Hypotheticals only — no state transitions, no desirability.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional
from enum import Enum


class SimulationType(Enum):
    """Types of simulation."""
    HYPOTHETICAL = "hypothetical"
    COUNTERFACTUAL = "counterfactual"
    EXPLORATORY = "exploratory"


@dataclass(frozen=True)
class HypotheticalScenario:
    """
    A hypothetical scenario for reasoning.
    
    Scenarios are descriptive, not prescriptive.
    """
    scenario_id: str
    description: str
    assumptions: tuple
    simulation_type: SimulationType
    created_at: datetime


@dataclass(frozen=True)
class SimulationResult:
    """
    Result of hypothetical reasoning.
    
    Results describe what MIGHT happen, not what SHOULD happen.
    """
    result_id: str
    scenario_id: str
    outcome_description: str
    reasoning_chain: tuple
    is_descriptive: bool  # Must always be True
    confidence: float


class PrescriptiveSimulationError(Exception):
    """Raised when simulation attempts prescriptive reasoning."""
    pass


class SimulationStub:
    """
    Hypothetical reasoning without action.
    
    Capabilities:
    - Hypothetical reasoning only
    - No state transitions
    - No evaluation of desirability
    
    Simulations are DESCRIPTIVE, not PRESCRIPTIVE.
    They describe what might be, not what should be done.
    """
    
    def __init__(self):
        """Initialize simulation stub."""
        self._scenarios: dict = {}
        self._results: List[SimulationResult] = []
    
    def create_scenario(
        self,
        description: str,
        assumptions: tuple,
        sim_type: SimulationType = SimulationType.HYPOTHETICAL,
    ) -> str:
        """
        Create a hypothetical scenario.
        
        Args:
            description: What if scenario
            assumptions: Assumptions being made
            sim_type: Type of simulation
            
        Returns:
            scenario_id
        """
        import hashlib
        
        scenario_id = hashlib.sha256(
            f"{description}:{assumptions}".encode()
        ).hexdigest()[:16]
        
        scenario = HypotheticalScenario(
            scenario_id=scenario_id,
            description=description,
            assumptions=assumptions,
            simulation_type=sim_type,
            created_at=datetime.utcnow(),
        )
        
        self._scenarios[scenario_id] = scenario
        return scenario_id
    
    def simulate(
        self,
        scenario_id: str,
        reasoning_steps: tuple,
    ) -> SimulationResult:
        """
        Run hypothetical simulation.
        
        Produces DESCRIPTIVE outcome only.
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        
        import hashlib
        result_id = hashlib.sha256(
            f"{scenario_id}:{reasoning_steps}".encode()
        ).hexdigest()[:16]
        
        # Generate descriptive outcome
        outcome = f"Given assumptions {scenario.assumptions}, the scenario '{scenario.description}' would result in: {reasoning_steps[-1] if reasoning_steps else 'unknown outcome'}"
        
        result = SimulationResult(
            result_id=result_id,
            scenario_id=scenario_id,
            outcome_description=outcome,
            reasoning_chain=reasoning_steps,
            is_descriptive=True,  # MUST be True
            confidence=0.5,  # Hypotheticals have moderate confidence
        )
        
        self._results.append(result)
        return result
    
    def evaluate_desirability(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Evaluate desirability of outcomes.
        
        Simulations are descriptive, not prescriptive.
        """
        raise PrescriptiveSimulationError(
            "Desirability evaluation is forbidden. "
            "Simulations describe what might happen, not what should happen."
        )
    
    def recommend_action(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Recommend actions.
        
        Simulation cannot prescribe actions.
        """
        raise PrescriptiveSimulationError(
            "Action recommendation is forbidden. "
            "Cognition has no authority to recommend actions."
        )
    
    def trigger_state_change(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Trigger state changes.
        
        Simulation is purely hypothetical.
        """
        raise PrescriptiveSimulationError(
            "State changes are forbidden. "
            "Simulation is purely hypothetical with no real effects."
        )
    
    def optimize_outcome(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Optimize outcomes.
        
        Cognition cannot optimize.
        """
        raise PrescriptiveSimulationError(
            "Outcome optimization is forbidden. "
            "Cognition describes, it does not optimize."
        )
    
    def get_scenario(self, scenario_id: str) -> Optional[HypotheticalScenario]:
        """Get scenario by ID."""
        return self._scenarios.get(scenario_id)
    
    def get_results_for_scenario(self, scenario_id: str) -> List[SimulationResult]:
        """Get all results for a scenario."""
        return [r for r in self._results if r.scenario_id == scenario_id]
    
    @property
    def scenario_count(self) -> int:
        """Number of scenarios."""
        return len(self._scenarios)
