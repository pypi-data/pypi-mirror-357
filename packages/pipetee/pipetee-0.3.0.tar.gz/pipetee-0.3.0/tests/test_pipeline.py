import asyncio
from typing import Any, Callable, List, Optional, Union, cast
from unittest.mock import MagicMock, patch

import pytest

from pipetee.models.stage import StageDecision, StageResult
from pipetee.pipeline import Condition, Pipeline, PipelineStage

# Type aliases for clarity
ConditionCallable = Callable[[Any], Union[bool, asyncio.Future[bool]]]


class SimpleStage(PipelineStage[str, str]):
    """Simple stage for testing"""

    async def process(self, data: str) -> StageResult[str]:
        self.logger.info("Processing data: %s", data)
        return StageResult(success=True, data=data + "_processed")


class AsyncStage(PipelineStage[str, str]):
    """Stage with configurable delay for testing async behavior"""

    def __init__(self, delay: float = 0.1, should_fail: bool = False) -> None:
        super().__init__()
        self.delay = delay
        self.should_fail = should_fail
        self.processed_count = 0

    async def process(self, data: str) -> StageResult[str]:
        self.logger.info("Processing data with delay: %s", data)
        await asyncio.sleep(self.delay)
        self.processed_count += 1

        if self.should_fail:
            return StageResult(success=False, data=None, error="Simulated failure")
        return StageResult(success=True, data=f"{data}_delayed_{self.processed_count}")


@pytest.mark.asyncio
async def test_pipeline_logging() -> None:
    """Test that pipeline logs appropriate messages"""
    with patch("pipetee.pipeline.setup_logger") as mock_logger_setup:
        # Create a mock logger
        mock_logger = MagicMock()
        mock_logger_setup.return_value = mock_logger

        # Initialize pipeline and add a stage
        pipeline = Pipeline()
        stage = SimpleStage()
        pipeline.add_stage("test_stage", stage)

        # Test initialization logs
        mock_logger.info.assert_any_call("Initializing new pipeline")
        mock_logger.info.assert_any_call("Adding stage: %s", "test_stage")

        # Process some data
        result = await pipeline.process("test_data")

        # Verify logging calls
        mock_logger.info.assert_any_call("Starting pipeline processing")
        mock_logger.debug.assert_any_call("Processing stage: %s", "test_stage")
        mock_logger.info.assert_any_call(
            "Pipeline processing completed in %s seconds",
            mock_logger.info.call_args.args[1],
        )
        assert isinstance(result.data, str)
        assert "processed" in result.data


@pytest.mark.asyncio
async def test_parallel_processing() -> None:
    """Test that multiple stages can process in parallel"""
    # Create stages with different delays
    stage1 = AsyncStage(delay=0.2)
    stage2 = AsyncStage(delay=0.1)
    stage3 = AsyncStage(delay=0.3)

    pipeline = Pipeline()
    pipeline.add_stage("stage1", stage1)
    pipeline.add_stage("stage2", stage2)
    pipeline.add_stage("stage3", stage3)

    # Process data and measure time
    start_time = asyncio.get_event_loop().time()
    result = await pipeline.process("test_data")
    end_time = asyncio.get_event_loop().time()

    # Total time should be less than sum of individual delays
    total_time = end_time - start_time
    assert total_time < 0.7  # Sum would be 0.6, allow some overhead
    assert result.success
    assert isinstance(result.data, str)
    assert "delayed" in result.data


@pytest.mark.asyncio
async def test_async_condition_chain() -> None:
    """Test chain of async conditions"""
    results: List[str] = []

    async def async_condition1(data: Any) -> bool:
        await asyncio.sleep(0.1)
        results.append("condition1")
        return True

    async def async_condition2(data: Any) -> bool:
        await asyncio.sleep(0.1)
        results.append("condition2")
        return False

    # Cast async functions to the expected condition type
    condition1 = cast(ConditionCallable, async_condition1)
    condition2 = cast(ConditionCallable, async_condition2)

    stage = AsyncStage(delay=0.1)
    stage.add_skip_condition(Condition("condition1", condition1))
    stage.add_skip_condition(Condition("condition2", condition2))

    pipeline = Pipeline()
    pipeline.add_stage("test_stage", stage)

    result = await pipeline.process("test_data")

    # Both conditions should have been evaluated in order
    assert results == [
        "condition1"
    ]  # Second condition shouldn't be called since first returns True
    assert result.success
    assert result.data == "test_data"  # Original data since stage was skipped


@pytest.mark.asyncio
async def test_async_error_propagation() -> None:
    """Test error handling in async stages"""
    error_stage = AsyncStage(delay=0.1, should_fail=True)
    success_stage = AsyncStage(delay=0.1)

    pipeline = Pipeline()
    pipeline.add_stage("error_stage", error_stage)
    pipeline.add_stage("success_stage", success_stage)

    result = await pipeline.process("test_data")

    assert not result.success
    assert result.error == "Simulated failure"
    assert success_stage.processed_count == 0  # Second stage should not have run


@pytest.mark.asyncio
async def test_async_branching() -> None:
    """Test async branching logic"""

    async def branch_condition(data: Any) -> bool:
        await asyncio.sleep(0.1)
        return isinstance(data, str) and "branch" in data

    # Cast async function to the expected condition type
    condition = cast(ConditionCallable, branch_condition)

    class BranchingStage(PipelineStage[str, str]):
        """Stage that can branch based on condition"""

        def __init__(self, condition: Condition, branch_target: str) -> None:
            super().__init__()
            self.branch_condition = condition
            self.branch_target = branch_target

        async def process(self, data: str) -> StageResult[str]:
            if await self.branch_condition.evaluate(data):
                return StageResult(
                    success=True,
                    data=data + "_branched",
                    decision=StageDecision.BRANCH_TO,
                    next_stage=self.branch_target,
                )
            # Add the transformation before continuing
            transformed_data = data + "_continued"
            return StageResult(success=True, data=transformed_data)

    # Create stages
    main_stage = BranchingStage(Condition("test_branch_data", condition), "branch")
    branch_stage = AsyncStage(delay=0.1)
    final_stage = AsyncStage(delay=0.1)

    # Setup pipeline with branching
    pipeline = Pipeline()
    pipeline.add_stage("main", main_stage)
    pipeline.add_stage("final", final_stage)
    pipeline.add_stage("branch", branch_stage)

    # Test branching path
    result1 = await pipeline.process("test_branch_data")
    assert result1.metadata is not None
    assert "branch" in result1.metadata["execution_path"]
    assert (
        "final" not in result1.metadata["execution_path"]
    )  # Should not hit final stage
    assert result1.data is not None
    assert isinstance(result1.data, str)
    assert result1.data.endswith("_branched_delayed_1")

    # Test normal path
    result2 = await pipeline.process("test_data")
    assert result2.metadata is not None
    assert "branch" in result2.metadata["execution_path"]
    assert "final" in result2.metadata["execution_path"]  # Should hit final stage
    assert result2.data is not None
    assert isinstance(result2.data, str)
    assert result2.data.endswith("_delayed_2")


@pytest.mark.asyncio
async def test_async_post_processors() -> None:
    """Test async post processors with varying delays"""
    results: List[str] = []

    async def slow_processor(data: str) -> str:
        await asyncio.sleep(0.2)
        results.append("slow")
        return data + "_slow"

    async def fast_processor(data: str) -> str:
        await asyncio.sleep(0.1)
        results.append("fast")
        return data + "_fast"

    stage = AsyncStage(delay=0.1)
    stage.add_post_processor(slow_processor)
    stage.add_post_processor(fast_processor)

    pipeline = Pipeline()
    pipeline.add_stage("test_stage", stage)

    result = await pipeline.process("test_data")

    # Post processors should run in sequence
    assert results == ["slow", "fast"]
    assert result.success
    assert isinstance(result.data, str)
    assert "_slow_fast" in result.data


@pytest.mark.asyncio
async def test_async_stage_decisions() -> None:
    """Test async stages with different flow control decisions"""

    class DecisionStage(PipelineStage[str, str]):
        def __init__(
            self,
            decision: StageDecision,
            next_stage: Optional[str] = None,
            name: str = "",
        ) -> None:
            super().__init__()
            self.stage_decision = decision
            self.next_stage_name = next_stage
            self.name = name

        async def process(self, data: str) -> StageResult[str]:
            print(f"Processing stage: {self.name} with decision: {self.stage_decision}")
            await asyncio.sleep(0.1)
            result = StageResult(
                success=True,
                data=f"{data}_{self.name}",
                decision=self.stage_decision,
                next_stage=self.next_stage_name,
            )
            print(f"Stage {self.name} completed with result: {result}")
            return result

    # Create pipeline with different decision stages
    pipeline = Pipeline()
    pipeline.add_stage(
        "continue", DecisionStage(StageDecision.CONTINUE, name="continue")
    )
    pipeline.add_stage(
        "skip_next", DecisionStage(StageDecision.SKIP_NEXT, name="skip_next")
    )
    pipeline.add_stage("skipped", DecisionStage(StageDecision.CONTINUE, name="skipped"))
    pipeline.add_stage(
        "jump", DecisionStage(StageDecision.JUMP_TO, "jump_target", name="jump")
    )
    pipeline.add_stage(
        "jump_target", DecisionStage(StageDecision.CONTINUE, name="jump_target")
    )
    pipeline.add_stage(
        "terminate", DecisionStage(StageDecision.TERMINATE, name="terminate")
    )

    print("\nStarting pipeline processing...")
    result = await pipeline.process("test_data")
    print(f"\nPipeline completed with result: {result}")

    assert result.success
    assert result.metadata is not None

    execution_path = result.metadata["execution_path"]
    print(f"\nExecution path: {execution_path}")

    # More specific assertions
    assert execution_path == [
        "continue",
        "skip_next",
        "jump",
        "jump_target",
        "terminate",
    ], f"Unexpected execution path: {execution_path}"
