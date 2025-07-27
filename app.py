import streamlit as st
import asyncio
from carrear_mate import (
    conversation_agent,
    Runner,
    MissingSkillsResponse,
    JobFinderResponse,
    CourseRecommendationsResponse
)

st.set_page_config(page_title="CareerMate", layout="centered")

st.title("💼 CareerMate – Multi-Agent Career Advisor")
st.markdown("Ask anything related to your career path, job search, or skill gaps.")

# Session state to keep history (optional)
if "history" not in st.session_state:
    st.session_state.history = []

# Text input from user
user_input = st.text_input("💬 Ask CareerMate...", placeholder="e.g., What skills do I need to become a data scientist?")

if st.button("Ask"):
    if user_input.strip():
        st.session_state.history.append(("You", user_input))
        st.write("🤖 CareerMate is thinking...")

        async def run_agent():
            result = await Runner.run(conversation_agent, user_input)
            return result.final_output

        # Run async function inside Streamlit
        output = asyncio.run(run_agent())

        # Display based on agent type
        if isinstance(output, MissingSkillsResponse):
            st.subheader("🛠 Missing Skills:")
            for skill in output.missing_skills:
                st.markdown(f"- {skill}")

        elif isinstance(output, JobFinderResponse):
            st.subheader("💼 Matching Jobs:")
            for job in output.jobs:
                st.markdown(f"**🔹 {job.title}** at *{job.company}* ({job.location})")
                st.markdown("Required Skills:")
                for skill in job.skills:
                    st.markdown(f"- {skill}")
                st.markdown("---")

        elif isinstance(output, CourseRecommendationsResponse):
            st.subheader("📚 Course Recommendations:")
            for skill_course in output.recommendations:
                st.markdown(f"**Skill:** {skill_course.skill}")
                for course in skill_course.courses:
                    st.markdown(f"• [{course.title}]({course.link}) on {course.platform}")
                st.markdown("---")

        else:
            st.error("CareerMate couldn't process your request. Please try again.")

