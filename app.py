import streamlit as st
import asyncio
from carrear_mate import (
    conversation_agent,
    Runner,
    MissingSkillsResponse,
    JobFinderResponse,
    CourseRecommendationsResponse
)

# ---- PAGE CONFIG ----
st.set_page_config(page_title="CareerMate", layout="centered")

# ---- TITLE ----
st.title("💼 CareerMate – Multi-Agent Career Advisor")
st.markdown("Helping you plan and grow your career intelligently 🚀")


# ---- THEME DETECTION ----
def inject_theme_css():
    css = """
    <style>
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        html, body, [class*="css"]  {
            transition: all 0.3s ease-in-out;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_theme_css()

# ---- GOAL SELECTOR ----
goal = st.selectbox(
    "🎯 What is your current goal?",
    [
        "Explore new career options",
        "Identify skills for a job",
        "Find matching jobs",
        "Get course recommendations",
        "Just browsing"
    ],
    index=1,
)

# ---- CHAT HISTORY STATE ----
if "history" not in st.session_state:
    st.session_state.history = []

# ---- SHOW CHAT HISTORY ----
for role, message in st.session_state.history:
    with st.chat_message(role.lower()):
        st.markdown(message)

# ---- USER INPUT ----
user_input = st.chat_input("Ask CareerMate something...")

if user_input:
    # Show user message
    st.session_state.history.append(("You", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("CareerMate is thinking..."):
            async def run_agent():
                result = await Runner.run(conversation_agent, user_input)
                return result.final_output

            output = asyncio.run(run_agent())

            # Build assistant response
            if isinstance(output, MissingSkillsResponse):
                response_md = "### 🛠 Missing Skills:\n" + "\n".join(f"- {skill}" for skill in output.missing_skills)

            elif isinstance(output, JobFinderResponse):
                response_md = "### 💼 Matching Jobs:\n"
                for job in output.jobs:
                    response_md += f"**🔹 {job.title}** at *{job.company}* ({job.location})\n"
                    response_md += "Required Skills:\n"
                    response_md += "\n".join(f"- {skill}" for skill in job.skills)
                    response_md += "\n---\n"

            elif isinstance(output, CourseRecommendationsResponse):
                response_md = "### 📚 Course Recommendations:\n"
                for skill_course in output.recommendations:
                    response_md += f"**Skill:** {skill_course.skill}\n"
                    for course in skill_course.courses:
                        response_md += f"• [{course.title}]({course.link}) on {course.platform}\n"
                    response_md += "---\n"

            else:
                response_md = "⚠️ CareerMate couldn't process your request. Please try again."

            st.markdown(response_md)
            st.session_state.history.append(("Assistant", response_md))
