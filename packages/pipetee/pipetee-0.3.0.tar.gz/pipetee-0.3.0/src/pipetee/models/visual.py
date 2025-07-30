"""
Models for pipeline visualization.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class StageVizInfo(BaseModel):
    """Information about a stage's visualization state."""

    name: str = Field(..., description="Name of the stage")
    status: str = Field(..., description="Current status of the stage")
    start_time: Optional[datetime] = Field(
        None, description="When stage started processing"
    )
    end_time: Optional[datetime] = Field(
        None, description="When stage finished processing"
    )
    error: Optional[str] = Field(None, description="Error message if stage failed")
    metrics: Optional[Dict[str, Any]] = Field(
        None, description="Stage-specific metrics"
    )
