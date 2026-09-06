"""
FastAPI routes — all REST endpoints for the placement interview system.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.models.schemas import (
    InterviewRequest, AnswerRequest, MCPToolRequest,
    ResumeFeedbackRequest, StudyPlanRequest,
    StartInterviewResponse, AnswerResponse, FeedbackResponse,
    MCPToolResponse, EvaluationResult, QuestionAnswer,
)
from app.models.session_manager import SessionManager
from app.agents.groq_client import GroqClient
from app.agents.interview_agent import InterviewAgent
from app.agents.feedback_agent import FeedbackAgent
from app.mcp.mcp_server import MCPServer

from .dependencies import (
    get_groq_client, get_mcp_server, get_session_manager, DummyRetriever
)

router = APIRouter()


# ── Health Check ─────────────────────────────────────────────

@router.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "Placement Interview AI"}


@router.get("/stats", tags=["System"])
def get_stats(sm: SessionManager = Depends(get_session_manager)):
    return sm.get_stats()


# ── Interview Endpoints ───────────────────────────────────────

@router.post("/interview/start", response_model=StartInterviewResponse, tags=["Interview"])
def start_interview(
    req: InterviewRequest,
    groq: GroqClient = Depends(get_groq_client),
    sm: SessionManager = Depends(get_session_manager),
):
    """Start a new mock interview session."""
    try:
        retriever = DummyRetriever()

        session = sm.create_session(
            candidate_name=req.candidate_name,
            position=req.position,
            difficulty=req.difficulty.value,
            total_questions=req.total_questions,
            round_type=req.round_type.value,
        )

        agent = InterviewAgent(
            groq_client=groq,
            retriever=retriever,
            difficulty=req.difficulty.value,
            total_questions=req.total_questions,
        )

        opening = agent.start_interview(req.position, req.candidate_name)
        first_question = agent.generate_question()

        session.current_question = first_question
        sm.update_session(session)
        sm.store_agent(session.session_id, agent)

        logger.info(f"Interview started: {session.session_id}")
        return StartInterviewResponse(
            session_id=session.session_id,
            opening_message=opening,
            first_question=first_question,
            session=session,
        )
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview/answer", response_model=AnswerResponse, tags=["Interview"])
def submit_answer(
    req: AnswerRequest,
    sm: SessionManager = Depends(get_session_manager),
):
    """Submit an answer to the current question."""
    session = sm.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail=f"Session is {session.status}")

    agent: InterviewAgent = sm.get_agent(req.session_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Interview agent not found")

    try:
        result = agent.process_answer(req.answer)
        eval_data = result["evaluation"]

        qa = QuestionAnswer(
            question_number=len(session.qa_history) + 1,
            question=agent.questions_asked[-2] if len(agent.questions_asked) > 1 else agent.questions_asked[-1],
            answer=req.answer,
            evaluation=EvaluationResult(**eval_data),
        )
        session.qa_history.append(qa)
        session.current_question = result.get("next_question")
        sm.update_session(session)

        if result["is_complete"]:
            report = agent.get_final_report()
            scores = [qa.evaluation.score for qa in session.qa_history if qa.evaluation]
            avg = sum(scores) / len(scores) if scores else 0
            sm.complete_session(req.session_id, report, avg)

        progress = (result["questions_asked"] / result["total_questions"]) * 100

        return AnswerResponse(
            evaluation=EvaluationResult(**eval_data),
            next_question=result.get("next_question"),
            is_complete=result["is_complete"],
            questions_asked=result["questions_asked"],
            total_questions=result["total_questions"],
            progress_percent=round(progress, 1),
        )
    except Exception as e:
        logger.error(f"Error processing answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interview/{session_id}", tags=["Interview"])
def get_session(session_id: str, sm: SessionManager = Depends(get_session_manager)):
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/interview/{session_id}/report", response_model=FeedbackResponse, tags=["Interview"])
def get_report(session_id: str, sm: SessionManager = Depends(get_session_manager)):
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    scores = [qa.evaluation.score for qa in session.qa_history if qa.evaluation]
    avg = sum(scores) / len(scores) if scores else 0

    return FeedbackResponse(
        session_id=session_id,
        final_report=session.final_report or "Report not available.",
        overall_score=session.overall_score or 0,
        total_questions=len(session.qa_history),
        average_score=round(avg, 2),
    )


@router.get("/sessions", tags=["Interview"])
def list_sessions(sm: SessionManager = Depends(get_session_manager)):
    return sm.list_sessions()


# ── MCP Tool Endpoints ────────────────────────────────────────

@router.get("/mcp/tools", tags=["MCP"])
def list_mcp_tools(mcp: MCPServer = Depends(get_mcp_server)):
    return {"tools": mcp.list_tools()}


@router.post("/mcp/call", response_model=MCPToolResponse, tags=["MCP"])
def call_mcp_tool(
    req: MCPToolRequest,
    mcp: MCPServer = Depends(get_mcp_server),
):
    result = mcp.call_tool(req.tool_name, req.arguments)
    success = "error" not in result
    return MCPToolResponse(
        tool_name=req.tool_name,
        result=result.get("result", result.get("error")),
        success=success,
        error=result.get("error"),
    )


# ── Feedback Endpoints ────────────────────────────────────────

@router.post("/feedback/resume", tags=["Feedback"])
def resume_feedback(
    req: ResumeFeedbackRequest,
    groq: GroqClient = Depends(get_groq_client),
):
    agent = FeedbackAgent(groq)
    feedback = agent.resume_feedback(req.resume_text, req.job_description)
    return {"feedback": feedback}


@router.post("/feedback/study-plan", tags=["Feedback"])
def generate_study_plan(
    req: StudyPlanRequest,
    groq: GroqClient = Depends(get_groq_client),
):
    agent = FeedbackAgent(groq)
    plan = agent.generate_study_plan(req.weak_topics, req.position, req.days)
    return {"study_plan": plan}


@router.post("/feedback/tip", tags=["Feedback"])
def get_tip(topic: str, groq: GroqClient = Depends(get_groq_client)):
    agent = FeedbackAgent(groq)
    return {"tip": agent.generate_tip(topic)}
