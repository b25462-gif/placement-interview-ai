"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class RoundType(str, Enum):
    technical = "Technical"
    behavioral = "Behavioral"
    hr = "HR"
    aptitude = "Aptitude"
    full = "Full"


# ── Request Models ──────────────────────────────────────────

class InterviewRequest(BaseModel):
    candidate_name: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=200)
    difficulty: Difficulty = Difficulty.medium
    total_questions: int = Field(10, ge=3, le=30)
    round_type: RoundType = RoundType.full
    resume_text: Optional[str] = Field(None, max_length=10000)
    job_description: Optional[str] = Field(None, max_length=5000)


class AnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(..., min_length=1, max_length=5000)


class MCPToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


class ResumeFeedbackRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=10000)
    job_description: str = Field(..., min_length=20, max_length=5000)


class StudyPlanRequest(BaseModel):
    weak_topics: List[str] = Field(..., min_length=1)
    position: str
    days: int = Field(14, ge=7, le=30)


# ── Data Models ──────────────────────────────────────────────

class EvaluationResult(BaseModel):
    score: int = Field(..., ge=1, le=10)
    strengths: List[str] = []
    improvements: List[str] = []
    ideal_answer_hint: str = ""
    follow_up: Optional[str] = None


class QuestionAnswer(BaseModel):
    question_number: int
    question: str
    answer: str
    question_type: str = "General"
    evaluation: Optional[EvaluationResult] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InterviewSession(BaseModel):
    session_id: str
    candidate_name: str
    position: str
    difficulty: Difficulty
    total_questions: int
    round_type: RoundType
    status: str = "active"          # active | completed | abandoned
    current_question: Optional[str] = None
    qa_history: List[QuestionAnswer] = []
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    final_report: Optional[str] = None
    overall_score: Optional[float] = None


# ── Response Models ──────────────────────────────────────────

class StartInterviewResponse(BaseModel):
    session_id: str
    opening_message: str
    first_question: str
    session: InterviewSession


class AnswerResponse(BaseModel):
    evaluation: EvaluationResult
    next_question: Optional[str]
    is_complete: bool
    questions_asked: int
    total_questions: int
    progress_percent: float


class FeedbackResponse(BaseModel):
    session_id: str
    final_report: str
    overall_score: float
    total_questions: int
    average_score: float


class MCPToolResponse(BaseModel):
    tool_name: str
    result: Any
    success: bool = True
    error: Optional[str] = None
