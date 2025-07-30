"""Unit tests for StageResult and StageDecision models."""

from typing import Dict

from pipetee.models.stage import StageDecision, StageResult


def test_stage_decision_enum() -> None:
    """Test StageDecision enum values and behavior."""
    assert StageDecision.CONTINUE.value == "continue"
    assert StageDecision.SKIP_NEXT.value == "skip_next"
    assert StageDecision.JUMP_TO.value == "jump_to"
    assert StageDecision.BRANCH_TO.value == "branch_to"
    assert StageDecision.TERMINATE.value == "terminate"


def test_stage_result_creation() -> None:
    """Test StageResult creation with different parameters."""
    # Test basic successful result
    result = StageResult[str](success=True, data="test_data")
    assert result.success is True
    assert result.data == "test_data"
    assert result.decision == StageDecision.CONTINUE
    assert result.next_stage is None
    assert result.error is None
    assert result.metadata is None

    # Test failed result with error
    result = StageResult[str](success=False, data=None, error="Something went wrong")
    assert result.success is False
    assert result.data is None
    assert result.error == "Something went wrong"


def test_stage_result_with_flow_control() -> None:
    """Test StageResult with different flow control decisions."""
    # Test JUMP_TO decision
    result = StageResult[str](
        success=True,
        data="test_data",
        decision=StageDecision.JUMP_TO,
        next_stage="target_stage",
    )
    assert result.decision == StageDecision.JUMP_TO
    assert result.next_stage == "target_stage"

    # Test BRANCH_TO decision with metadata
    result = StageResult[str](
        success=True,
        data="test_data",
        decision=StageDecision.BRANCH_TO,
        next_stage="new_branch",
        metadata={"reason": "condition_met"},
    )
    assert result.decision == StageDecision.BRANCH_TO
    assert result.next_stage == "new_branch"
    assert result.metadata == {"reason": "condition_met"}


def test_stage_result_type_hints() -> None:
    """Test StageResult with different type parameters."""
    # Test with int type
    result_int = StageResult[int](success=True, data=42)
    assert isinstance(result_int.data, int)

    # Test with dict type
    result_dict = StageResult[Dict[str, str]](success=True, data={"key": "value"})
    assert isinstance(result_dict.data, dict)

    # Test with None data
    result_none = StageResult[str](success=False, data=None)
    assert result_none.data is None
