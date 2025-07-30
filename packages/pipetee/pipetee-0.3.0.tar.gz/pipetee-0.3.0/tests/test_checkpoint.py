"""
Tests for pipeline checkpoint functionality.
"""

import json
import shutil
from pathlib import Path
from typing import Generator

import pytest

from pipetee.models.stage import StageResult
from pipetee.pipeline import Pipeline, PipelineStage


class SimpleStage(PipelineStage[int, int]):
    """A simple stage that increments input by 1."""

    async def process(self, data: int) -> StageResult[int]:
        return StageResult(success=True, data=data + 1)


class FailingStage(PipelineStage[int, int]):
    """A stage that fails after N successful runs."""

    def __init__(self, fail_after: int = 1):
        super().__init__()
        self.fail_after = fail_after
        self.runs = 0  # Track runs per instance

    async def process(self, data: int) -> StageResult[int]:
        self.runs += 1
        if self.runs >= self.fail_after:
            return StageResult(success=False, data=None, error="Simulated failure")
        return StageResult(success=True, data=data + 1)


@pytest.fixture(autouse=True)
def cleanup_checkpoints() -> Generator[None, None, None]:
    """Clean up checkpoint directory before and after each test."""
    checkpoint_dir = Path(".pipeline_checkpoints")
    if checkpoint_dir.exists():
        shutil.rmtree(checkpoint_dir)
    checkpoint_dir.mkdir()
    yield
    if checkpoint_dir.exists():
        shutil.rmtree(checkpoint_dir)


@pytest.fixture
def checkpoint_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for checkpoints."""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    return checkpoint_dir


@pytest.fixture
def simple_pipeline(checkpoint_dir: Path) -> Pipeline:
    """Create a simple pipeline with three stages."""
    pipeline = Pipeline()
    pipeline._checkpoint_dir = checkpoint_dir

    pipeline.add_stage("stage1", SimpleStage())
    pipeline.add_stage("stage2", SimpleStage())
    pipeline.add_stage("stage3", SimpleStage())

    return pipeline


@pytest.mark.asyncio
async def test_checkpoint_creation(
    simple_pipeline: Pipeline, checkpoint_dir: Path
) -> None:
    """Test creating a checkpoint."""
    # Process data until stage2
    checkpoint = await simple_pipeline.create_checkpoint("stage2", 2, 1)

    # Verify checkpoint file exists
    checkpoint_path = checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
    assert checkpoint_path.exists()

    # Verify checkpoint content
    with open(checkpoint_path) as f:
        data = json.load(f)
        assert data["current_stage"] == "stage2"
        assert data["current_data"] == 2
        assert data["input_data"] == 1


@pytest.mark.asyncio
async def test_pipeline_restore(simple_pipeline: Pipeline) -> None:
    """Test restoring pipeline state from checkpoint."""
    # Create a checkpoint
    checkpoint = await simple_pipeline.create_checkpoint("stage2", 2, 1)

    # Restore from checkpoint and continue processing
    result = await simple_pipeline.restore_from_checkpoint(checkpoint.checkpoint_id)

    # Final result should be 4 (input=1, +1 from stage1, +1 from stage2, +1 from stage3)
    assert result == 4


@pytest.mark.asyncio
async def test_automatic_checkpoint_on_failure() -> None:
    """Test that checkpoints are automatically created on stage failure."""
    pipeline = Pipeline()
    pipeline.add_stage("stage1", SimpleStage())
    pipeline.add_stage("stage2", FailingStage(fail_after=1))
    pipeline.add_stage("stage3", SimpleStage())

    # First run should fail at stage2 and create checkpoint
    result = await pipeline.process(1)
    assert not result.success
    assert result.error == "Simulated failure"

    # Verify checkpoint was created
    checkpoints = list(pipeline._checkpoint_dir.glob("*.json"))
    assert len(checkpoints) == 1

    # Load checkpoint data
    with open(checkpoints[0]) as f:
        data = json.load(f)
        assert data["current_stage"] == "stage2"
        assert data["current_data"] == 2  # Input 1 + 1 from stage1


@pytest.mark.asyncio
async def test_restore_and_continue_execution() -> None:
    """Test restoring from a checkpoint and continuing execution."""
    pipeline = Pipeline()
    failing_stage = FailingStage(fail_after=2)  # Fails after 2 runs

    pipeline.add_stage("stage1", SimpleStage())
    pipeline.add_stage("stage2", failing_stage)  # Use the same instance
    pipeline.add_stage("stage3", SimpleStage())

    # First run should succeed
    result = await pipeline.process(1)
    assert result.success
    assert result.data == 4  # 1 + 1 + 1 + 1

    # Second run should fail at stage2
    result = await pipeline.process(1)
    assert not result.success
    assert result.error == "Simulated failure"

    # Get the checkpoint ID
    checkpoints = list(pipeline._checkpoint_dir.glob("*.json"))
    assert len(checkpoints) == 1
    checkpoint_id = checkpoints[0].stem

    # Create a new pipeline with the same stages
    restore_pipeline = Pipeline()
    restore_pipeline._checkpoint_dir = pipeline._checkpoint_dir
    restore_pipeline.add_stage("stage1", SimpleStage())
    restore_pipeline.add_stage("stage2", FailingStage(fail_after=2))  # New instance
    restore_pipeline.add_stage("stage3", SimpleStage())

    # Restore and continue - should succeed because it's a new instance
    final_data = await restore_pipeline.restore_from_checkpoint(checkpoint_id)
    assert isinstance(final_data, int)
    assert final_data == 4  # Should complete successfully
