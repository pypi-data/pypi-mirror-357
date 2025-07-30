from dataclasses import dataclass, field
from typing import List

from iwf.workflow_state import WorkflowState


@dataclass
class StateDef:
    state: WorkflowState
    can_start_workflow: bool

    @classmethod
    def starting_state(cls, state: WorkflowState):
        return StateDef(state, True)

    @classmethod
    def non_starting_state(cls, state: WorkflowState):
        return StateDef(state, False)


@dataclass
class StateSchema:
    states: List[StateDef] = field(default_factory=list)

    # TODO: it's super weird that we can't use type hint here " ->StateSchema" for return
    # But the pattern works for state_movement.py
    @classmethod
    def with_starting_state(
        cls, starting_state: WorkflowState, *non_starting_states: WorkflowState
    ):
        return StateSchema(
            [StateDef.starting_state(starting_state)]
            + [StateDef.non_starting_state(s) for s in non_starting_states]
        )

    @classmethod
    def no_starting_state(cls, *non_starting_states: WorkflowState):
        return StateSchema(
            [StateDef.non_starting_state(s) for s in non_starting_states]
        )
