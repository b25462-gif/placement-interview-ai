"""
Interview Agent — conducts AI-powered mock placement interviews.
Uses Groq LLM + RAG context to generate smart, personalized questions.
"""

from typing import List, Dict, Optional
from loguru import logger

from .groq_client import GroqClient
from app.rag.retriever import RAGRetriever


SYSTEM_PROMPT = """You are an expert placement interviewer at a top tech company.
Your job is to conduct a professional mock interview for a student.

Guidelines:
- Ask ONE question at a time
- Questions should be relevant to the job description and student's resume
- Vary between: Technical, Behavioral, Situational, and HR questions
- Difficulty: {difficulty}
- Be encouraging but professional
- Do NOT give away answers

Current Interview Context:
- Position: {position}
- Round: {round_type}
- Questions asked so far: {questions_asked}/{total_questions}
"""

QUESTION_PROMPT = """
Based on the following context, generate the next interview question.

Student Resume Context:
{resume_context}

Job Description Context:
{jd_context}

Previous Questions Asked:
{previous_questions}

Generate exactly ONE {question_type} interview question.
Make it specific, relevant, and {difficulty} level.
Return only the question, nothing else.
"""

EVALUATION_PROMPT = """
You are evaluating a student's interview answer.

Question: {question}
Student's Answer: {answer}

Job Description Context:
{jd_context}

Evaluate the answer and respond in this exact JSON format:
{{
  "score": <1-10>,
  "strengths": ["point1", "point2"],
  "improvements": ["point1", "point2"],
  "ideal_answer_hint": "brief hint about what a great answer includes",
  "follow_up": "one follow-up question based on their answer"
}}
"""


class InterviewAgent:
    QUESTION_TYPES = ["Technical", "Behavioral", "Situational", "HR", "Problem-Solving"]

    def __init__(
        self,
        groq_client: GroqClient,
        retriever: RAGRetriever,
        difficulty: str = "medium",
        total_questions: int = 10,
    ):
        self.groq = groq_client
        self.retriever = retriever
        self.difficulty = difficulty
        self.total_questions = total_questions
        self.conversation_history: List[Dict[str, str]] = []
        self.questions_asked: List[str] = []
        self.current_round = "Technical"

    def start_interview(self, position: str, candidate_name: str) -> str:
        """Generate the interview opening message."""
        self.position = position
        self.candidate_name = candidate_name

        opening = self.groq.simple_prompt(
            system="You are a warm, professional placement interviewer.",
            user=f"""Write a friendly interview opening for:
- Candidate: {candidate_name}
- Position: {position}
- Interview type: Campus Placement Mock Interview

Keep it to 3-4 sentences. End with asking them to introduce themselves."""
        )
        self.conversation_history.append({"role": "assistant", "content": opening})
        return opening

    def generate_question(self) -> str:
        """Generate the next interview question using RAG context."""
        q_num = len(self.questions_asked)
        q_type = self.QUESTION_TYPES[q_num % len(self.QUESTION_TYPES)]

        resume_ctx = self.retriever.get_resume_context(self.position)
        jd_ctx = self.retriever.get_jd_context(self.position)
        prev_qs = "\n".join(f"{i+1}. {q}" for i, q in enumerate(self.questions_asked)) or "None yet"

        prompt = QUESTION_PROMPT.format(
            resume_context=resume_ctx,
            jd_context=jd_ctx,
            previous_questions=prev_qs,
            question_type=q_type,
            difficulty=self.difficulty,
        )
        system = SYSTEM_PROMPT.format(
            difficulty=self.difficulty,
            position=self.position,
            round_type=q_type,
            questions_asked=q_num,
            total_questions=self.total_questions,
        )

        question = self.groq.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ])

        self.questions_asked.append(question)
        self.conversation_history.append({"role": "assistant", "content": question})
        logger.info(f"Generated Q{q_num+1} ({q_type}): {question[:60]}...")
        return question

    def evaluate_answer(self, question: str, answer: str) -> Dict:
        """Evaluate a student's answer and return structured feedback."""
        jd_ctx = self.retriever.get_jd_context(self.position)

        prompt = EVALUATION_PROMPT.format(
            question=question,
            answer=answer,
            jd_context=jd_ctx,
        )
        raw = self.groq.simple_prompt(
            system="You are an expert interview evaluator. Always respond with valid JSON only.",
            user=prompt,
        )

        try:
            import json
            # Extract JSON from response
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except Exception as e:
            logger.error(f"Failed to parse evaluation JSON: {e}")
            return {
                "score": 5,
                "strengths": ["Attempted the question"],
                "improvements": ["Be more specific"],
                "ideal_answer_hint": "Review the topic and try again.",
                "follow_up": "Can you elaborate on that?",
            }

    def process_answer(self, answer: str) -> Dict:
        """Process the latest answer and return evaluation + next question."""
        if not self.questions_asked:
            return {"error": "No question has been asked yet."}

        current_question = self.questions_asked[-1]
        self.conversation_history.append({"role": "user", "content": answer})

        evaluation = self.evaluate_answer(current_question, answer)

        is_complete = len(self.questions_asked) >= self.total_questions
        next_question = None if is_complete else self.generate_question()

        return {
            "evaluation": evaluation,
            "next_question": next_question,
            "is_complete": is_complete,
            "questions_asked": len(self.questions_asked),
            "total_questions": self.total_questions,
        }

    def get_final_report(self) -> str:
        """Generate a comprehensive final interview report."""
        return self.groq.simple_prompt(
            system="You are an expert career counselor generating a detailed interview report.",
            user=f"""Generate a comprehensive placement interview report for:
- Candidate: {self.candidate_name}
- Position: {self.position}
- Total Questions: {len(self.questions_asked)}
- Difficulty: {self.difficulty}

Questions covered:
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(self.questions_asked))}

Provide:
1. Overall Performance Summary
2. Key Strengths (3-4 points)
3. Areas for Improvement (3-4 points)
4. Topic-wise readiness (Technical, Communication, Problem-Solving)
5. Final Recommendation (Ready / Needs More Prep / Not Ready)
6. Study Plan for next 2 weeks

Format it professionally."""
        )
