"""
Session Manager — in-memory store for active interview sessions.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional
from loguru import logger

from .schemas import InterviewSession, Difficulty, RoundType


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, InterviewSession] = {}
        self._agents: Dict[str, object] = {}  # session_id -> InterviewAgent
        logger.info("SessionManager initialized.")

    def create_session(
        self,
        candidate_name: str,
        position: str,
        difficulty: str = "medium",
        total_questions: int = 10,
        round_type: str = "Full",
    ) -> InterviewSession:
        session_id = str(uuid.uuid4())
        session = InterviewSession(
            session_id=session_id,
            candidate_name=candidate_name,
            position=position,
            difficulty=Difficulty(difficulty),
            total_questions=total_questions,
            round_type=RoundType(round_type),
            status="active",
        )
        self._sessions[session_id] = session
        logger.info(f"Session created: {session_id} | {candidate_name} | {position}")
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self._sessions.get(session_id)

    def update_session(self, session: InterviewSession) -> None:
        self._sessions[session.session_id] = session

    def complete_session(self, session_id: str, final_report: str, overall_score: float) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.final_report = final_report
            session.overall_score = overall_score
            logger.info(f"Session completed: {session_id} | score={overall_score:.1f}")

    def store_agent(self, session_id: str, agent: object) -> None:
        self._agents[session_id] = agent

    def get_agent(self, session_id: str) -> Optional[object]:
        return self._agents.get(session_id)

    def list_sessions(self) -> list[InterviewSession]:
        return list(self._sessions.values())

    def delete_session(self, session_id: str) -> bool:
        removed = self._sessions.pop(session_id, None)
        self._agents.pop(session_id, None)
        return removed is not None

    def get_stats(self) -> dict:
        sessions = list(self._sessions.values())
        completed = [s for s in sessions if s.status == "completed"]
        avg_score = (
            sum(s.overall_score for s in completed if s.overall_score) / len(completed)
            if completed else 0
        )
        return {
            "total_sessions": len(sessions),
            "active": sum(1 for s in sessions if s.status == "active"),
            "completed": len(completed),
            "average_score": round(avg_score, 2),
        }


# Singleton instance
session_manager = SessionManager()
