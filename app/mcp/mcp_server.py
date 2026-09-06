"""
MCP Server — exposes interview tools via Model Context Protocol.
Tools: search_questions, evaluate_answer, get_study_tip, search_resume, search_jd
"""

import json
import asyncio
from typing import Any
from loguru import logger

# MCP tool registry
_tools: dict[str, callable] = {}


def mcp_tool(name: str, description: str, input_schema: dict):
    """Decorator to register a function as an MCP tool."""
    def decorator(func):
        _tools[name] = {
            "function": func,
            "description": description,
            "input_schema": input_schema,
        }
        return func
    return decorator


class MCPServer:
    """
    Lightweight MCP-compatible server that wraps interview AI tools.
    Communicates via JSON over HTTP (SSE-compatible endpoint).
    """

    def __init__(self, name: str, retriever=None, groq_client=None):
        self.name = name
        self.retriever = retriever
        self.groq_client = groq_client
        self._register_tools()
        logger.info(f"MCP Server '{name}' initialized with {len(_tools)} tools.")

    def _register_tools(self):
        """Register all tools with access to retriever and groq."""
        retriever = self.retriever
        groq = self.groq_client

        @mcp_tool(
            name="search_interview_questions",
            description="Search the question bank for relevant interview questions by topic.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to search questions for"},
                    "count": {"type": "integer", "description": "Number of questions to return", "default": 5},
                },
                "required": ["topic"],
            },
        )
        def search_interview_questions(topic: str, count: int = 5) -> str:
            if retriever:
                ctx = retriever.get_question_context(topic)
                return ctx[:2000]
            return f"Sample questions for {topic}: 1. Explain {topic} basics. 2. Give an example of {topic}."

        @mcp_tool(
            name="search_resume",
            description="Search through uploaded resumes for relevant information.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for in resumes"},
                },
                "required": ["query"],
            },
        )
        def search_resume(query: str) -> str:
            if retriever:
                return retriever.get_resume_context(query)
            return "No resume data available."

        @mcp_tool(
            name="search_job_description",
            description="Search job descriptions for requirements and skills.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Job role or skill to search"},
                },
                "required": ["query"],
            },
        )
        def search_job_description(query: str) -> str:
            if retriever:
                return retriever.get_jd_context(query)
            return "No job description data available."

        @mcp_tool(
            name="get_interview_tip",
            description="Get a quick interview tip for a specific topic or skill.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic for the tip (e.g. arrays, STAR method, salary negotiation)"},
                },
                "required": ["topic"],
            },
        )
        def get_interview_tip(topic: str) -> str:
            if groq:
                return groq.simple_prompt(
                    system="You are a placement expert. Give 3 concise interview tips.",
                    user=f"Give 3 quick tips for: {topic}"
                )
            return f"Tip for {topic}: Practice consistently, use examples, and stay confident."

        @mcp_tool(
            name="evaluate_answer_quick",
            description="Quickly evaluate an interview answer and give a score.",
            input_schema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The interview question"},
                    "answer": {"type": "string", "description": "The student's answer"},
                },
                "required": ["question", "answer"],
            },
        )
        def evaluate_answer_quick(question: str, answer: str) -> str:
            if groq:
                return groq.simple_prompt(
                    system="You are an interview evaluator. Be concise.",
                    user=f"Question: {question}\n\nAnswer: {answer}\n\nGive: Score (1-10), 2 strengths, 2 improvements. Be brief."
                )
            return "Score: 7/10. Good attempt. Be more specific with examples."

    def list_tools(self) -> list[dict]:
        """Return all registered tools in MCP format."""
        return [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["input_schema"],
            }
            for name, info in _tools.items()
        ]

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Execute a registered tool by name."""
        if tool_name not in _tools:
            return {"error": f"Tool '{tool_name}' not found. Available: {list(_tools.keys())}"}
        try:
            result = _tools[tool_name]["function"](**arguments)
            logger.info(f"MCP tool called: {tool_name}")
            return {"result": result}
        except Exception as e:
            logger.error(f"MCP tool error ({tool_name}): {e}")
            return {"error": str(e)}


def create_mcp_server(name: str, retriever=None, groq_client=None) -> MCPServer:
    return MCPServer(name=name, retriever=retriever, groq_client=groq_client)
