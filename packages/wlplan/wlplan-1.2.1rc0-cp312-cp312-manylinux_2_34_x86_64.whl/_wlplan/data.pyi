from __future__ import annotations
import _wlplan.planning
__all__ = ['Dataset', 'ProblemStates']
class Dataset:
    """
    WLPlan dataset object.
    
    Datasets contain a domain and a list of problem states.
    
    Parameters
    ----------
        domain : Domain
            Domain object.
    
        data : list[ProblemStates]
            List of problem states.
    """
    def __init__(self, domain: _wlplan.planning.Domain, data: list[...]) -> None:
        ...
class ProblemStates:
    """
    Stores a problem and training states for the problem.
    
    Upon initialisation, the problem and states are checked for consistency.
    
    Parameters
    ----------
        problem : Problem
            Problem object.
    
        states : list[State]
            List of training states.
    """
    def __init__(self, problem: _wlplan.planning.Problem, states: list[_wlplan.planning.State]) -> None:
        ...
    @property
    def problem(self) -> _wlplan.planning.Problem:
        ...
    @property
    def states(self) -> list[_wlplan.planning.State]:
        ...
