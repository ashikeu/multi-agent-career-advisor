import asyncio
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from pydantic import BaseModel

# Load environment variables (for OpenAI or replace with your model info)
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError("Please set BASE_URL, API_KEY, and MODEL_NAME.")

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


class MissingSkillsResponse(BaseModel):
    missing_skills: List[str]

class JobListing(BaseModel):
    title: str
    company: str
    location: str
    skills: List[str]

class JobFinderResponse(BaseModel):
    jobs: List[JobListing]

class Course(BaseModel):
    title: str
    platform: str
    link: str

class SkillCourse(BaseModel):
    skill: str
    courses: List[Course]

class CourseRecommendationsResponse(BaseModel):
    recommendations: List[SkillCourse]


# ----------- Dummy Data -------------

JOB_SKILLS = {
    "data scientist": ["Python", "SQL", "Statistics", "Machine Learning", "Pandas"],
    "data analyst": ["Excel", "SQL", "Tableau", "Statistics"],
    "software engineer": ["Python", "Algorithms", "Data Structures", "Git"],
    "web developer": ["HTML", "CSS", "JavaScript", "React"],
    "frontend developer": ["HTML", "CSS", "JavaScript", "Vue.js"],
    "backend developer": ["Node.js", "MongoDB", "REST APIs", "Express.js"],
    "machine learning engineer": ["Python", "TensorFlow", "Scikit-learn", "Numpy"],
    "ai researcher": ["Deep Learning", "PyTorch", "Python", "Research Skills"],
    "data engineer": ["SQL", "Spark", "Airflow", "ETL Pipelines"],
    "devops engineer": ["Docker", "Kubernetes", "CI/CD", "Linux"],
    "product manager": ["Agile", "Wireframing", "Communication", "JIRA"],
    "mobile app developer": ["Flutter", "Dart", "Firebase", "UI Design"],
    "cloud engineer": ["AWS", "Terraform", "Docker", "Networking"],
    "business analyst": ["Excel", "SQL", "Power BI", "Stakeholder Communication"],
    "cybersecurity analyst": ["Network Security", "SIEM", "Python", "Incident Response"],
    "systems analyst": ["Systems Design", "UML", "SQL", "Documentation"],
    "full stack developer": ["JavaScript", "React", "Node.js", "SQL"],
    "database administrator": ["SQL", "Oracle", "Backup and Recovery", "Performance Tuning"],
    "qa engineer": ["Test Cases", "Selenium", "JIRA", "Automation Testing"],
    "computer vision engineer": ["OpenCV", "Deep Learning", "Python", "Image Processing"]
}


JOB_LISTINGS = [
    {"title": "Junior Data Scientist", "company": "DataCorp", "location": "New York", "skills": ["Python", "SQL", "Machine Learning"]},
    {"title": "Data Analyst", "company": "Analytics LLC", "location": "San Francisco", "skills": ["Excel", "SQL", "Tableau"]},
    {"title": "Software Engineer", "company": "TechSoft", "location": "Remote", "skills": ["Python", "Git", "Data Structures"]},
    {"title": "Frontend Developer", "company": "WebWorks", "location": "Boston", "skills": ["HTML", "CSS", "JavaScript"]},
    {"title": "Machine Learning Engineer", "company": "AI Labs", "location": "Seattle", "skills": ["Python", "TensorFlow", "Data Preprocessing"]},
    {"title": "Business Intelligence Analyst", "company": "Insight Co", "location": "Chicago", "skills": ["SQL", "Power BI", "Excel"]},
    {"title": "Backend Developer", "company": "CodeBase", "location": "Austin", "skills": ["Node.js", "MongoDB", "APIs"]},
    {"title": "DevOps Engineer", "company": "Cloudify", "location": "Remote", "skills": ["Docker", "Kubernetes", "CI/CD"]},
    {"title": "Product Manager", "company": "StartupX", "location": "Los Angeles", "skills": ["Agile", "Roadmapping", "Communication"]},
    {"title": "Full Stack Developer", "company": "Buildify", "location": "Denver", "skills": ["React", "Node.js", "SQL"]},
    {"title": "AI Researcher", "company": "DeepThink", "location": "Boston", "skills": ["Deep Learning", "Python", "PyTorch"]},
    {"title": "Data Engineer", "company": "DataFlow Inc.", "location": "New York", "skills": ["Spark", "Airflow", "SQL"]},
    {"title": "Mobile App Developer", "company": "Appify", "location": "San Diego", "skills": ["Flutter", "Dart", "Firebase"]},
    {"title": "Cybersecurity Analyst", "company": "SecureNet", "location": "Dallas", "skills": ["Networking", "SIEM", "Python"]},
    {"title": "Systems Analyst", "company": "IT Solutions", "location": "Philadelphia", "skills": ["Systems Design", "SQL", "UML"]}
]


COURSES = {
    "Python": [
        {
            "title": "Python for Everybody",
            "platform": "Coursera",
            "link": "https://coursera.org/python"
        },
        {
            "title": "Automate the Boring Stuff",
            "platform": "Udemy",
            "link": "https://udemy.com/automate"
        }
    ],
    "SQL": [
        {
            "title": "SQL Basics",
            "platform": "Codecademy",
            "link": "https://codecademy.com/sql"
        }
    ],
    "Statistics": [
        {
            "title": "Intro to Statistics",
            "platform": "Khan Academy",
            "link": "https://khanacademy.org/statistics"
        }
    ],
    "Machine Learning": [
        {
            "title": "Machine Learning by Andrew Ng",
            "platform": "Coursera",
            "link": "https://coursera.org/ml"
        }
    ],
    "Pandas": [
        {
            "title": "Data Analysis with Pandas",
            "platform": "DataCamp",
            "link": "https://datacamp.com/pandas"
        }
    ],
    "Excel": [
        {
            "title": "Excel Essentials",
            "platform": "LinkedIn Learning",
            "link": "https://linkedin.com/learning/excel"
        }
    ],
    "Tableau": [
        {
            "title": "Getting Started with Tableau",
            "platform": "Udemy",
            "link": "https://udemy.com/tableau"
        }
    ],
    "Git": [
        {
            "title": "Git Fundamentals",
            "platform": "Pluralsight",
            "link": "https://pluralsight.com/git"
        }
    ],
    "JavaScript": [
        {
            "title": "JavaScript Basics",
            "platform": "FreeCodeCamp",
            "link": "https://freecodecamp.org/js"
        }
    ],
    "React": [
        {
            "title": "React for Beginners",
            "platform": "Udemy",
            "link": "https://udemy.com/react-for-beginners"
        }
    ]
}


# ------------ Tools -------------

@function_tool
def get_missing_skills(user_skills: List[str], target_job: str) -> MissingSkillsResponse:
    """Compare user skills with required job skills and return missing skills."""
    required = JOB_SKILLS.get(target_job.lower())
    if not required:
        return MissingSkillsResponse(missing_skills=[])
    missing = [skill for skill in required if skill not in user_skills]
    return MissingSkillsResponse(missing_skills=missing)




@function_tool
def find_jobs(user_skills: List[str], location: Optional[str] = None) -> JobFinderResponse:
    matching_jobs = []
    for job in JOB_LISTINGS:
        skill_matches = len(set(user_skills).intersection(set(job["skills"])))
        if skill_matches >= len(job["skills"]) // 2:
            if location is None or location.lower() in job["location"].lower():
                matching_jobs.append(JobListing(**job))
    return JobFinderResponse(jobs=matching_jobs)



# @function_tool
# def recommend_courses(missing_skills: List[str]) -> CourseRecommendationsResponse:
#     """Recommend courses for each missing skill."""
#     recommendations = {}
#     for skill in missing_skills:
#         courses = COURSES.get(skill, [])
#         course_models = [Course(**course) for course in courses]
#         if course_models:
#             recommendations[skill] = course_models
#     return CourseRecommendationsResponse(recommendations=recommendations)

@function_tool
def recommend_courses(missing_skills: List[str]) -> CourseRecommendationsResponse:
    recommendations = []
    for skill in missing_skills:
        courses = COURSES.get(skill, [])
        course_models = [Course(**course) for course in courses]
        if course_models:
            recommendations.append(SkillCourse(skill=skill, courses=course_models))
    return CourseRecommendationsResponse(recommendations=recommendations)



# ------------- Agents -------------

skill_gap_agent = Agent(
    name="Skill Gap Agent",
    handoff_description="Helps identify missing skills for a target job role",
    instructions="""
    You help the user find what skills they are missing for their desired job.
    Use the get_missing_skills tool to compare user's current skills and target job.
    Present missing skills clearly.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_missing_skills],
    output_type=MissingSkillsResponse,
)

job_finder_agent = Agent(
    name="Job Finder Agent",
    handoff_description="Specialist agent for finding relevant jobs based on skills and location",
    instructions="""
    You are a job finder specialist who suggests job openings based on user's skills and preferred location.
    Provide clear job details including title, company, location, and required skills.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[find_jobs],
    output_type=JobFinderResponse
)

course_recommender_agent = Agent(
    name="Course Recommender Agent",
    handoff_description="Specialist agent recommending courses for missing skills",
    instructions="""You are a course recommender who suggests online courses to learn skills the user is missing.
    Provide course title, platform, and links for each missing skill.""",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[recommend_courses],
    output_type=CourseRecommendationsResponse,  # ✅ This must match actual return
)


# conversation_agent = Agent(
#     name="Conversation Agent",
#     instructions="""...""",
#     model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
#     handoffs=[skill_gap_agent, job_finder_agent, course_recommender_agent],
#     # ✅ REMOVE THIS LINE:
#     # output_type=object,
# )


conversation_agent = Agent(
    name="Conversation Agent",
   instructions = """
You are CareerMate, a career advisor assistant that routes queries to these agents:
- Skill Gap Agent: Identifies missing skills given current skills and job target.
- Job Finder Agent: Finds jobs matching user's skills and location.
- Course Recommender Agent: Recommends courses for missing skills.

Carefully choose which agent to use based on user's request.
Respond only with the output of the selected agent, not explanations.
""",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    handoffs=[skill_gap_agent, job_finder_agent, course_recommender_agent],
    output_type=None,
)

# ----------- Main -----------------

async def main():
    print("Welcome to CareerMate - Your Multi-Agent Career Advisor!\n")

    # Example interactive loop (can extend to real CLI or UI)
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        print("\n[CareerMate is thinking...]\n")

        result = await Runner.run(conversation_agent, user_input)

        # Show which agent handled it (for demo, assume logs inside the framework)
        # Display the structured output if possible:
        output = result.final_output
        if isinstance(output, MissingSkillsResponse):
            print("🛠 Skill Gap Agent identified missing skills:")
            for skill in output.missing_skills:
                print(f"- {skill}")

        elif isinstance(output, JobFinderResponse):
            print("💼 Job Finder Agent found these jobs:")
            for job in output.jobs:
                print(f"\n🔹 {job.title} at {job.company} ({job.location})")
                print("   Required Skills:")
                for skill in job.skills:
                    print(f"   - {skill}")

        elif isinstance(output, CourseRecommendationsResponse):
            print("📚 Course Recommender Agent suggests:")
            for skill_course in output.recommendations:
                print(f"  For skill '{skill_course.skill}':")
                for course in skill_course.courses:
                    print(f"    • {course.title} on {course.platform}: {course.link}")


        else:
            print("🤖 CareerMate couldn't process your request. Please try again.")

        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
