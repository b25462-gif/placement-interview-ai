"""
Streamlit Frontend — Student Placement Interview AI
Full interactive UI with interview, feedback, resume analyzer, and study plan.
"""

import streamlit as st
import requests
import json
from datetime import datetime

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="🎯 Placement Interview AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000/api/v1"


# ── Helper Functions ──────────────────────────────────────────
def api_post(endpoint: str, data: dict) -> dict | None:
    try:
        res = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=180)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure the API server is running on port 8000.")
        return None
    except requests.exceptions.ReadTimeout:
        st.error("⏳ Request timed out. The AI is taking longer than usual. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return None


def api_get(endpoint: str) -> dict | None:
    try:
        res = requests.get(f"{API_BASE}{endpoint}", timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def score_color(score: int) -> str:
    if score >= 8:
        return "🟢"
    elif score >= 5:
        return "🟡"
    return "🔴"


# ── CSS Styling ───────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        background: #1e1e2e;
        border-left: 4px solid #667eea;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
    }
    .eval-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    .score-badge {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/goal.png", width=64)
    st.title("🎯 Interview AI")
    st.caption("Powered by Groq + RAG + MCP")
    st.divider()

    page = st.radio(
        "Navigate",
        ["🏠 Home", "🎤 Mock Interview", "📄 Resume Analyzer", "📚 Study Plan", "🔧 MCP Tools", "📊 Dashboard"],
        label_visibility="collapsed",
    )

    st.divider()
    # Backend status
    health = api_get("/health")
    if health:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Offline")


# ── HOME PAGE ─────────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Student Placement Interview AI</h1>
        <p>Your personal AI-powered placement preparation coach</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🤖 AI Model", "Llama 3.3 70B")
    col2.metric("🧠 RAG", "ChromaDB")
    col3.metric("🔧 MCP Tools", "5 Tools")
    col4.metric("📊 Evaluation", "Real-time")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 What can I do?")
        st.markdown("""
        - **Mock Interviews** — Full placement-style interview sessions
        - **Smart Questions** — Generated from your resume & JD using RAG
        - **Answer Evaluation** — Real-time scoring with feedback
        - **Resume Analysis** — AI review against job description
        - **Study Plans** — Personalized 14-day prep plan
        - **MCP Tools** — Direct access to AI interview tools
        """)

    with col2:
        st.subheader("📋 How to start?")
        st.markdown("""
        1. Go to **🎤 Mock Interview**
        2. Enter your name and target position
        3. Choose difficulty and number of questions
        4. Start the interview!
        5. Get detailed feedback after every answer
        6. Download your final report
        """)

    st.info("💡 Tip: Upload your resume and JD in the data folders for personalized questions!")


# ── MOCK INTERVIEW PAGE ───────────────────────────────────────
elif page == "🎤 Mock Interview":
    st.title("🎤 Mock Interview")

    # Initialize session state
    if "interview_active" not in st.session_state:
        st.session_state.interview_active = False
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "is_complete" not in st.session_state:
        st.session_state.is_complete = False

    # ── Setup Form ────────────────────────────────────────────
    if not st.session_state.interview_active:
        st.subheader("⚙️ Interview Setup")

        with st.form("interview_setup"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Your Name", placeholder="e.g. Rahul Sharma")
                position = st.text_input("💼 Target Position", placeholder="e.g. Software Engineer at Google")
            with col2:
                difficulty = st.selectbox("🎯 Difficulty", ["easy", "medium", "hard"], index=1)
                total_q = st.slider("❓ Number of Questions", 3, 20, 10)

            round_type = st.selectbox(
                "🔄 Interview Round",
                ["Full", "Technical", "Behavioral", "HR", "Aptitude"],
            )

            submitted = st.form_submit_button("🚀 Start Interview", use_container_width=True)

        if submitted:
            if not name or not position:
                st.warning("Please fill in your name and target position!")
            else:
                with st.spinner("🤖 Starting your interview..."):
                    result = api_post("/interview/start", {
                        "candidate_name": name,
                        "position": position,
                        "difficulty": difficulty,
                        "total_questions": total_q,
                        "round_type": round_type,
                    })

                if result:
                    st.session_state.interview_active = True
                    st.session_state.session_id = result["session_id"]
                    st.session_state.current_question = result["first_question"]
                    st.session_state.chat_history = [
                        {"role": "assistant", "content": result["opening_message"]},
                        {"role": "assistant", "content": f"**Question 1:** {result['first_question']}"},
                    ]
                    st.session_state.is_complete = False
                    st.rerun()

    # ── Active Interview ──────────────────────────────────────
    else:
        session = api_get(f"/interview/{st.session_state.session_id}")
        if session:
            progress = len(session.get("qa_history", [])) / session["total_questions"]
            st.progress(progress, text=f"Progress: {len(session.get('qa_history', []))}/{session['total_questions']} questions")

        # Chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

        if not st.session_state.is_complete:
            # Answer input
            answer = st.chat_input("Type your answer here...")

            if answer:
                st.session_state.chat_history.append({"role": "user", "content": answer})

                with st.spinner("🤔 Evaluating your answer..."):
                    result = api_post("/interview/answer", {
                        "session_id": st.session_state.session_id,
                        "answer": answer,
                    })

                if result:
                    eval_data = result["evaluation"]
                    score = eval_data["score"]
                    emoji = score_color(score)

                    # Evaluation feedback
                    feedback_msg = f"""
**{emoji} Score: {score}/10**

✅ **Strengths:**
{chr(10).join(f"• {s}" for s in eval_data.get("strengths", []))}

📈 **Improvements:**
{chr(10).join(f"• {i}" for i in eval_data.get("improvements", []))}

💡 **Hint:** {eval_data.get("ideal_answer_hint", "")}
"""
                    st.session_state.chat_history.append({"role": "assistant", "content": feedback_msg})

                    if result["is_complete"]:
                        st.session_state.is_complete = True
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "🎉 **Interview Complete!** Click below to see your full report."
                        })
                    else:
                        next_q = result.get("next_question", "")
                        q_num = result["questions_asked"] + 1
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"**Question {q_num}:** {next_q}"
                        })
                        st.session_state.current_question = next_q

                    st.rerun()

        else:
            # Show report button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 View Full Report", use_container_width=True):
                    report = api_get(f"/interview/{st.session_state.session_id}/report")
                    if report:
                        st.subheader("📊 Final Interview Report")
                        st.metric("Overall Score", f"{report['overall_score']:.1f}/10")
                        st.metric("Average Score", f"{report['average_score']:.1f}/10")
                        st.markdown(report["final_report"])
            with col2:
                if st.button("🔄 New Interview", use_container_width=True):
                    st.session_state.interview_active = False
                    st.session_state.session_id = None
                    st.session_state.current_question = None
                    st.session_state.chat_history = []
                    st.session_state.is_complete = False
                    st.rerun()


# ── RESUME ANALYZER PAGE ──────────────────────────────────────
elif page == "📄 Resume Analyzer":
    st.title("📄 Resume Analyzer")
    st.caption("Get AI-powered feedback on your resume against a job description")

    col1, col2 = st.columns(2)
    with col1:
        resume_text = st.text_area(
            "📋 Paste Your Resume",
            height=300,
            placeholder="Paste your resume text here...",
        )
    with col2:
        jd_text = st.text_area(
            "💼 Paste Job Description",
            height=300,
            placeholder="Paste the job description here...",
        )

    if st.button("🔍 Analyze Resume", use_container_width=True):
        if not resume_text or not jd_text:
            st.warning("Please provide both resume and job description!")
        else:
            with st.spinner("🤖 Analyzing your resume..."):
                result = api_post("/feedback/resume", {
                    "resume_text": resume_text,
                    "job_description": jd_text,
                })
            if result:
                st.subheader("📊 Analysis Results")
                st.markdown(result["feedback"])


# ── STUDY PLAN PAGE ───────────────────────────────────────────
elif page == "📚 Study Plan":
    st.title("📚 Personalized Study Plan")

    with st.form("study_plan_form"):
        position = st.text_input("💼 Target Position", placeholder="e.g. Data Scientist")
        weak_topics = st.text_area(
            "📌 Weak Topics (one per line)",
            placeholder="Data Structures\nSystem Design\nSQL\nMachine Learning",
            height=150,
        )
        days = st.slider("📅 Study Duration (days)", 7, 30, 14)
        submitted = st.form_submit_button("📚 Generate Study Plan", use_container_width=True)

    if submitted:
        topics = [t.strip() for t in weak_topics.strip().split("\n") if t.strip()]
        if not position or not topics:
            st.warning("Please fill in position and at least one topic!")
        else:
            with st.spinner("🤖 Creating your personalized study plan..."):
                result = api_post("/feedback/study-plan", {
                    "position": position,
                    "weak_topics": topics,
                    "days": days,
                })
            if result:
                st.subheader(f"📅 Your {days}-Day Study Plan")
                st.markdown(result["study_plan"])


# ── MCP TOOLS PAGE ────────────────────────────────────────────
elif page == "🔧 MCP Tools":
    st.title("🔧 MCP Tool Explorer")
    st.caption("Model Context Protocol — direct access to AI interview tools")

    tools_data = api_get("/mcp/tools")
    if tools_data:
        tools = tools_data.get("tools", [])
        st.success(f"✅ {len(tools)} tools available")

        selected_tool = st.selectbox(
            "Select a Tool",
            [t["name"] for t in tools],
            format_func=lambda x: f"🔧 {x}",
        )

        tool_info = next((t for t in tools if t["name"] == selected_tool), None)
        if tool_info:
            st.info(f"📖 **Description:** {tool_info['description']}")

            st.subheader("⚙️ Tool Arguments")
            props = tool_info.get("inputSchema", {}).get("properties", {})
            args = {}
            for param, schema in props.items():
                desc = schema.get("description", param)
                if schema.get("type") == "integer":
                    args[param] = st.number_input(f"{param}", value=schema.get("default", 5))
                else:
                    args[param] = st.text_input(f"{param}", placeholder=desc)

            if st.button("▶️ Run Tool", use_container_width=True):
                # Filter empty args
                clean_args = {k: v for k, v in args.items() if v}
                with st.spinner("Running tool..."):
                    result = api_post("/mcp/call", {
                        "tool_name": selected_tool,
                        "arguments": clean_args,
                    })
                if result:
                    st.subheader("📤 Result")
                    if result["success"]:
                        st.markdown(str(result["result"]))
                    else:
                        st.error(f"Tool error: {result['error']}")


# ── DASHBOARD PAGE ────────────────────────────────────────────
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    stats = api_get("/stats")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📋 Total Sessions", stats["total_sessions"])
        col2.metric("🟢 Active", stats["active"])
        col3.metric("✅ Completed", stats["completed"])
        col4.metric("⭐ Avg Score", f"{stats['average_score']}/10")

    st.divider()
    st.subheader("📋 All Sessions")
    sessions = api_get("/sessions")
    if sessions:
        for s in sessions:
            with st.expander(f"🎤 {s['candidate_name']} — {s['position']} [{s['status'].upper()}]"):
                col1, col2, col3 = st.columns(3)
                col1.write(f"**Difficulty:** {s['difficulty']}")
                col2.write(f"**Questions:** {len(s.get('qa_history', []))}/{s['total_questions']}")
                col3.write(f"**Score:** {s.get('overall_score', 'N/A')}")
                if s.get("final_report"):
                    if st.button(f"View Report", key=s["session_id"]):
                        st.markdown(s["final_report"])
    else:
        st.info("No interview sessions yet. Start your first interview!")
