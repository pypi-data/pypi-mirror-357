"""Tests for the PipelineVisualizer class."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from pipetee.models.stage import StageResult
from pipetee.pipeline import Pipeline


@pytest.fixture
def pipeline() -> Pipeline:
    """Create a pipeline with some stages."""
    pipeline = Pipeline()

    # Create mock stages with process method
    async def mock_process(data: str) -> StageResult[str]:
        return StageResult(success=True, data=data + "_processed")

    pipeline.stages = {
        name: MagicMock(process=mock_process) for name in ["stage1", "stage2", "stage3"]
    }
    pipeline.default_sequence = ["stage1", "stage2", "stage3"]
    return pipeline


def test_visualizer_init(pipeline: Pipeline) -> None:
    """Test visualizer initialization."""
    assert pipeline.visualizer.viz_data == {}
    assert pipeline.visualizer._status_icons["pending"] == "🔄"
    assert pipeline.visualizer._status_icons["running"] == "⚡"
    assert pipeline.visualizer._status_icons["completed"] == "✅"
    assert pipeline.visualizer._status_icons["skipped"] == "⏭️"
    assert pipeline.visualizer._status_icons["failed"] == "❌"


def test_update_stage_status(pipeline: Pipeline) -> None:
    """Test updating stage status and info."""
    start_time = datetime.now()
    end_time = datetime.now()

    # Test adding new stage info
    pipeline.visualizer.update_stage_status(
        "stage1", "running", start_time=start_time, end_time=end_time
    )

    assert "stage1" in pipeline.visualizer.viz_data
    stage_info = pipeline.visualizer.viz_data["stage1"]
    assert stage_info.status == "running"
    assert stage_info.start_time == start_time
    assert stage_info.end_time == end_time

    # Test updating existing stage info
    pipeline.visualizer.update_stage_status("stage1", "completed")
    assert pipeline.visualizer.viz_data["stage1"].status == "completed"

    # Test invalid stage name
    with pytest.raises(ValueError, match="Invalid stage name"):
        pipeline.visualizer.update_stage_status("invalid_stage", "running")


def test_reset_visualization(pipeline: Pipeline) -> None:
    """Test resetting visualization data."""
    # Add some data
    pipeline.visualizer.update_stage_status("stage1", "running")
    pipeline.visualizer.update_stage_status("stage2", "completed")
    assert len(pipeline.visualizer.viz_data) == 2

    # Reset and verify
    pipeline.visualizer.reset()
    assert len(pipeline.visualizer.viz_data) == 0


def test_generate_mermaid_diagram(pipeline: Pipeline) -> None:
    """Test Mermaid.js diagram generation."""
    # Setup stage statuses
    pipeline.visualizer.update_stage_status("stage1", "completed")
    pipeline.visualizer.update_stage_status("stage2", "running")
    pipeline.visualizer.update_stage_status("stage3", "pending")

    diagram = pipeline.visualizer.generate_mermaid_diagram()

    # Verify diagram structure
    assert diagram.startswith("graph LR")
    assert "stage1" in diagram
    assert "stage2" in diagram
    assert "stage3" in diagram
    assert "-->" in diagram  # Verify connections
    assert "✅" in diagram  # Completed status icon
    assert "⚡" in diagram  # Running status icon
    assert "🔄" in diagram  # Pending status icon


def test_generate_execution_timeline(pipeline: Pipeline) -> None:
    """Test execution timeline generation."""
    start_time = datetime.now()
    end_time = datetime.now()

    # Setup stage execution times
    pipeline.visualizer.update_stage_status(
        "stage1", "completed", start_time=start_time, end_time=end_time
    )

    timeline = pipeline.visualizer.generate_execution_timeline()

    # Verify timeline structure
    assert timeline.startswith("gantt")
    assert "Pipeline Execution Timeline" in timeline
    assert "stage1" in timeline
    assert start_time.strftime("%H:%M:%S") in timeline
    assert end_time.strftime("%H:%M:%S") in timeline


def test_escape_mermaid_string(pipeline: Pipeline) -> None:
    """Test Mermaid string escaping."""
    assert pipeline.visualizer._escape_mermaid_string("test stage") == "test_stage"
    assert pipeline.visualizer._escape_mermaid_string("test-stage") == "test_stage"
    assert pipeline.visualizer._escape_mermaid_string("test_stage") == "test_stage"


@pytest.mark.asyncio
async def test_visualization_during_pipeline_execution(pipeline: Pipeline) -> None:
    """Test that visualization is updated correctly during pipeline execution."""
    # Process data through pipeline
    result = await pipeline.process("test_data")
    assert result.success

    # Verify visualization states
    assert all(stage in pipeline.visualizer.viz_data for stage in pipeline.stages)

    # All stages should be marked as completed after successful execution
    for stage_info in pipeline.visualizer.viz_data.values():
        assert stage_info.status == "completed"
        assert stage_info.start_time is not None
        assert stage_info.end_time is not None
        assert stage_info.error is None
