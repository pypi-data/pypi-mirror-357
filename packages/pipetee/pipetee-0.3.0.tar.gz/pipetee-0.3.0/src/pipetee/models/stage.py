from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generic, Optional, TypeVar

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class StageDecision(Enum):
    """Enum for stage execution decisions"""

    CONTINUE = "continue"  # Continue to next stage
    SKIP_NEXT = "skip_next"  # Skip the next stage
    JUMP_TO = "jump_to"  # Jump to a specific stage
    BRANCH_TO = "branch_to"  # Take a different branch
    PARALLEL_TO = "parallel_to"  # Execute multiple stages in parallel
    TERMINATE = "terminate"  # End pipeline processing


@dataclass
class StageResult(Generic[OutputType]):
    """Enhanced result with flow control decisions"""

    success: bool
    data: Optional[OutputType]
    decision: StageDecision = StageDecision.CONTINUE
    next_stage: Optional[str] = None  # For JUMP_TO and BRANCH_TO
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
