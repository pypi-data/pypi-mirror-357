"""
Models for pipeline checkpointing functionality.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelineCheckpoint(BaseModel):
    """Model representing a pipeline checkpoint."""

    checkpoint_id: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"),
        description="Unique identifier for the checkpoint",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the checkpoint was created"
    )
    current_stage: Optional[str] = Field(
        None, description="Name of the stage where execution was paused"
    )
    stage_states: Dict[str, Any] = Field(
        default_factory=dict, description="State data for each stage"
    )
    execution_path: List[str] = Field(
        default_factory=list, description="List of stages executed so far"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the checkpoint"
    )
    input_data: Any = Field(None, description="The initial input data to the pipeline")
    current_data: Any = Field(None, description="The current data being processed")
