"""
Feedback Agent — generates detailed personalized feedback and study plans.
"""

from loguru import logger
from .groq_client import GroqClient


class FeedbackAgent:
    def __init__(self, groq_client: GroqClient):
        self.groq = groq_client

    def generate_study_plan(self, weak_topics: list[str], position: str, days: int = 14) -> str:
        return self.groq.simple_prompt(
            system="You are an expert placement trainer and career coach.",
            user=f"""Create a detailed {days}-day study plan for a student preparing for {position}.

Weak areas identified: {', '.join(weak_topics)}

Include:
- Daily schedule (morning/evening topics)
- Resources (books, websites, practice problems)
- Mock interview milestones
- Quick revision tips

Format as a clean, readable plan."""
        )

    def analyze_communication(self, answer: str) -> dict:
        """Analyze communication quality of an answer."""
        raw = self.groq.simple_prompt(
            system="You are a communication skills expert. Respond only in JSON.",
            user=f"""Analyze the communication quality of this interview answer:

"{answer}"

Respond in JSON:
{{
  "clarity_score": <1-10>,
  "confidence_score": <1-10>,
  "structure_score": <1-10>,
  "vocabulary_score": <1-10>,
  "suggestions": ["tip1", "tip2", "tip3"]
}}"""
        )
        try:
            import json
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            return {
                "clarity_score": 5,
                "confidence_score": 5,
                "structure_score": 5,
                "vocabulary_score": 5,
                "suggestions": ["Speak more clearly", "Structure your answer using STAR method", "Use specific examples"],
            }

    def generate_tip(self, topic: str) -> str:
        """Generate a quick interview tip for a topic."""
        return self.groq.simple_prompt(
            system="You are a placement expert. Give concise, practical tips.",
            user=f"Give 3 quick interview tips for the topic: {topic}. Keep each tip under 2 sentences."
        )

    def resume_feedback(self, resume_text: str, job_description: str) -> str:
        """Provide resume improvement suggestions."""
        return self.groq.simple_prompt(
            system="You are a professional resume reviewer and career coach.",
            user=f"""Review this student resume against the job description and provide feedback.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1000]}

Provide:
1. Resume Score (out of 10)
2. What's Good (3 points)
3. What to Improve (3 points)
4. Missing Keywords
5. One-line Summary"""
        )
