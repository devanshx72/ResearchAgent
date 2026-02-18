"""
Pydantic models for API request/response schemas.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ExportFormat(str, Enum):
    """Supported export formats."""
    markdown = "markdown"
    md = "md"
    docx = "docx"
    notion = "notion"


class Tone(str, Enum):
    """Article tone options."""
    professional = "professional"
    casual = "casual"
    technical = "technical"


class TaskStatus(str, Enum):
    """Research task status."""
    pending = "pending"
    processing = "processing"
    hitl_review = "hitl_review"
    completed = "completed"
    failed = "failed"


class ResearchRequest(BaseModel):
    """Request model for starting a research task."""
    query: str = Field(..., description="Research topic or question")
    export_format: ExportFormat = Field(
        default=ExportFormat.markdown,
        description="Output format"
    )
    tone: Tone = Field(
        default=Tone.professional,
        description="Article tone"
    )
    word_count: int = Field(
        default=1000,
        ge=500,
        le=2000,
        description="Target word count"
    )


class ResearchResponse(BaseModel):
    """Response model for research task creation."""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus
    message: str


class HITLDecision(str, Enum):
    """Human decision options at HITL checkpoint."""
    approve = "approve"
    edit = "edit"
    reject = "reject"


class HITLResumeRequest(BaseModel):
    """Request model for resuming from HITL checkpoint."""
    decision: HITLDecision
    feedback: Optional[str] = Field(
        default=None,
        description="Optional feedback for edit/reject decisions"
    )


class TaskStatusResponse(BaseModel):
    """Response model for task status queries."""
    task_id: str
    status: TaskStatus
    current_node: Optional[str] = None
    progress: Optional[dict] = None
    article_draft: Optional[str] = None
    quality_score: Optional[float] = None
    sources: Optional[List[str]] = None
    error: Optional[str] = None


class TaskResultResponse(BaseModel):
    """Response model for completed task results."""
    task_id: str
    status: TaskStatus
    final_article: str
    export_path: str
    download_url: Optional[str] = Field(
        default=None,
        description="URL to download the exported file directly"
    )
    sources: List[str]
    quality_score: float


class WebSocketMessage(BaseModel):
    """WebSocket message model for real-time updates."""
    task_id: str
    event_type: str  # 'node_complete', 'status_update', 'error', 'hitl_checkpoint'
    data: dict
