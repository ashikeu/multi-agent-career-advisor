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
    "data analyst": ["Excel", "SQL", "Tableau", "Power BI", "Statistics"],
    "software engineer": ["Python", "Java", "Algorithms", "Data Structures", "Git"],
    "web developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "mobile app developer": ["Flutter", "React Native", "Dart", "Kotlin", "Swift"],
    "backend developer": ["Node.js", "Express", "MongoDB", "SQL", "REST APIs"],
    "frontend developer": ["HTML", "CSS", "JavaScript", "React", "Vue.js"],
    "cloud engineer": ["AWS", "Azure", "Docker", "Kubernetes", "Terraform"],
    "devops engineer": ["CI/CD", "Jenkins", "GitLab", "Docker", "Kubernetes"],
    "machine learning engineer": ["Python", "TensorFlow", "PyTorch", "ML Algorithms", "Data Processing"],
    "AI engineer": ["Deep Learning", "NLP", "Computer Vision", "Python", "Transformers"],
    "database administrator": ["SQL", "Oracle", "PostgreSQL", "Backup & Recovery", "Performance Tuning"],
    "network engineer": ["TCP/IP", "Routing", "Switching", "Firewalls", "Cisco"],
    "cybersecurity analyst": ["Firewalls", "Network Security", "SIEM", "Ethical Hacking", "Incident Response"],
    "product manager": ["Agile", "Scrum", "Roadmapping", "Wireframing", "Stakeholder Management"],
    "project manager": ["Project Planning", "Risk Management", "MS Project", "Agile", "Scrum"],
    "UI/UX designer": ["Figma", "Adobe XD", "User Research", "Prototyping", "Design Thinking"],
    "graphic designer": ["Photoshop", "Illustrator", "InDesign", "Branding", "Typography"],
    "business analyst": ["Requirement Gathering", "SQL", "Stakeholder Communication", "Process Modeling", "Excel"],
    "QA tester": ["Manual Testing", "Selenium", "JIRA", "Bug Tracking", "Test Automation"],
    "game developer": ["Unity", "C#", "Unreal Engine", "Game Design", "3D Modeling"],
    "embedded systems engineer": ["C", "C++", "Microcontrollers", "RTOS", "I2C/SPI"],
    "AI researcher": ["Deep Learning", "Research Writing", "Python", "Reinforcement Learning", "Mathematical Modeling"],
    "blockchain developer": ["Solidity", "Ethereum", "Smart Contracts", "Web3.js", "Cryptography"],
    "full stack developer": ["JavaScript", "React", "Node.js", "MongoDB", "Express.js"],
    "systems analyst": ["Systems Design", "SQL", "Testing", "Documentation", "Communication"],
    "IT support specialist": ["Windows", "Troubleshooting", "Helpdesk", "Networking", "Customer Service"],
    "digital marketer": ["SEO", "Google Analytics", "Social Media", "Email Marketing", "Content Creation"],
    "content writer": ["SEO Writing", "Blogging", "Copywriting", "Grammar", "Editing"],
    "HR manager": ["Recruiting", "HRIS", "Employee Relations", "Onboarding", "Compliance"],
    "accountant": ["Tally", "Excel", "Bookkeeping", "Taxation", "QuickBooks"],
    "financial analyst": ["Excel", "Forecasting", "Budgeting", "SQL", "Financial Modeling"],
    "civil engineer": ["AutoCAD", "Structural Design", "Surveying", "Construction Management", "Estimation"],
    "mechanical engineer": ["SolidWorks", "Thermodynamics", "CAD", "ANSYS", "Manufacturing Processes"],
    "electrical engineer": ["MATLAB", "Circuit Design", "Power Systems", "PLC", "Control Systems"],
    "biomedical engineer": ["Medical Devices", "Regulatory Compliance", "Signal Processing", "Bioinformatics", "LabVIEW"],
    "chemical engineer": ["Process Engineering", "Simulations", "Heat Transfer", "CHEMCAD", "Safety Standards"],
    "civil draftsman": ["AutoCAD", "Construction Drawings", "Survey Layout", "Blueprint Reading", "SketchUp"],
    "teacher": ["Lesson Planning", "Classroom Management", "Assessment", "Subject Knowledge", "Communication"],
    "sales executive": ["CRM", "Negotiation", "Lead Generation", "Customer Relationship", "Target Achievement"],
    "customer service rep": ["Communication", "CRM Tools", "Problem Solving", "Multitasking", "Patience"],
    "legal advisor": ["Legal Research", "Drafting", "Litigation", "Contract Law", "Negotiation"],
    "medical assistant": ["Vital Signs", "Patient Records", "Phlebotomy", "Clinical Procedures", "Medical Terminology"],
    "nurse": ["Patient Care", "IV Insertion", "EMR", "Medication Administration", "CPR"],
    "pharmacist": ["Prescription Review", "Pharmacology", "Drug Dispensing", "Inventory", "Patient Counseling"],
    "architect": ["AutoCAD", "SketchUp", "Design Principles", "Building Codes", "3D Modeling"],
    "interior designer": ["Space Planning", "AutoCAD", "Color Theory", "Material Selection", "Budget Management"],
    "logistics manager": ["Supply Chain", "Inventory", "Shipping", "ERP Systems", "Vendor Management"],
    "event planner": ["Budgeting", "Vendor Coordination", "Scheduling", "Marketing", "Creativity"],
}



JOB_LISTINGS = [
    {"title": "Junior Data Scientist", "company": "DataCorp", "location": "New York", "skills": ["Python", "SQL", "Machine Learning"]},
    {"title": "Software Engineer", "company": "TechNova", "location": "San Francisco", "skills": ["Java", "Spring Boot", "Git"]},
    {"title": "Data Analyst", "company": "Insights Inc", "location": "Chicago", "skills": ["Excel", "SQL", "Power BI"]},
    {"title": "Frontend Developer", "company": "WebWorks", "location": "Austin", "skills": ["HTML", "CSS", "React"]},
    {"title": "Backend Developer", "company": "CodeBase", "location": "Seattle", "skills": ["Node.js", "Express", "MongoDB"]},
    {"title": "Full Stack Developer", "company": "DevStudio", "location": "Remote", "skills": ["React", "Node.js", "PostgreSQL"]},
    {"title": "UI/UX Designer", "company": "DesignEdge", "location": "Boston", "skills": ["Figma", "User Research", "Prototyping"]},
    {"title": "DevOps Engineer", "company": "CloudCore", "location": "Denver", "skills": ["Docker", "Kubernetes", "CI/CD"]},
    {"title": "Mobile App Developer", "company": "Appify", "location": "Los Angeles", "skills": ["Flutter", "Dart", "Firebase"]},
    {"title": "Cloud Engineer", "company": "SkyNet", "location": "San Jose", "skills": ["AWS", "Terraform", "Python"]},
    {"title": "Cybersecurity Analyst", "company": "SecureTech", "location": "Atlanta", "skills": ["SIEM", "Firewalls", "Ethical Hacking"]},
    {"title": "AI Engineer", "company": "NeuroNet", "location": "New York", "skills": ["Deep Learning", "NLP", "TensorFlow"]},
    {"title": "Machine Learning Engineer", "company": "AlgoWorks", "location": "Remote", "skills": ["Scikit-learn", "XGBoost", "Python"]},
    {"title": "QA Tester", "company": "TestLogic", "location": "Dallas", "skills": ["Selenium", "Manual Testing", "JIRA"]},
    {"title": "Business Analyst", "company": "BizBridge", "location": "Philadelphia", "skills": ["SQL", "Requirement Gathering", "Excel"]},
    {"title": "Project Manager", "company": "ManageRight", "location": "Houston", "skills": ["Agile", "Scrum", "MS Project"]},
    {"title": "Product Manager", "company": "ProdVision", "location": "San Diego", "skills": ["Roadmaps", "Wireframes", "Scrum"]},
    {"title": "Graphic Designer", "company": "PixelPerfect", "location": "Miami", "skills": ["Photoshop", "Illustrator", "Branding"]},
    {"title": "Database Administrator", "company": "DataKeepers", "location": "Phoenix", "skills": ["PostgreSQL", "Backups", "SQL Tuning"]},
    {"title": "Network Engineer", "company": "NetFlow", "location": "Charlotte", "skills": ["TCP/IP", "Cisco", "Firewalls"]},
    {"title": "Content Writer", "company": "WritePro", "location": "Remote", "skills": ["SEO", "Blogging", "Grammar"]},
    {"title": "Digital Marketer", "company": "AdSync", "location": "Orlando", "skills": ["SEO", "Google Ads", "Analytics"]},
    {"title": "Sales Executive", "company": "SellFast", "location": "Houston", "skills": ["CRM", "Lead Generation", "Negotiation"]},
    {"title": "Customer Support Specialist", "company": "HelpMate", "location": "Remote", "skills": ["Communication", "Zendesk", "Patience"]},
    {"title": "Financial Analyst", "company": "FinSight", "location": "New York", "skills": ["Excel", "Budgeting", "Forecasting"]},
    {"title": "HR Manager", "company": "PeoplePros", "location": "Chicago", "skills": ["Recruitment", "Onboarding", "Compliance"]},
    {"title": "Accounting Assistant", "company": "BookKeepers Inc", "location": "Los Angeles", "skills": ["Tally", "Tax Filing", "Excel"]},
    {"title": "Embedded Systems Engineer", "company": "EmbedCore", "location": "San Jose", "skills": ["C", "Microcontrollers", "RTOS"]},
    {"title": "Legal Advisor", "company": "LawTech", "location": "Washington, D.C.", "skills": ["Contract Law", "Litigation", "Legal Drafting"]},
    {"title": "Civil Engineer", "company": "BuildMax", "location": "Denver", "skills": ["AutoCAD", "Surveying", "Construction Management"]},
    {"title": "Mechanical Engineer", "company": "MechaWorks", "location": "Detroit", "skills": ["SolidWorks", "Thermodynamics", "CAD"]},
    {"title": "Electrical Engineer", "company": "VoltPro", "location": "Austin", "skills": ["Circuit Design", "MATLAB", "PLC"]},
    {"title": "Biomedical Engineer", "company": "BioMedix", "location": "Boston", "skills": ["Signal Processing", "Medical Devices", "LabVIEW"]},
    {"title": "Event Planner", "company": "Eventix", "location": "Las Vegas", "skills": ["Scheduling", "Coordination", "Budgeting"]},
    {"title": "Logistics Manager", "company": "ShipQuick", "location": "Atlanta", "skills": ["Supply Chain", "Inventory", "ERP"]},
    {"title": "Architect", "company": "DesignArc", "location": "San Francisco", "skills": ["SketchUp", "AutoCAD", "3D Modeling"]},
    {"title": "Interior Designer", "company": "DecoSpace", "location": "New York", "skills": ["Color Theory", "Space Planning", "CAD"]},
    {"title": "Blockchain Developer", "company": "BlockForge", "location": "Remote", "skills": ["Solidity", "Smart Contracts", "Web3.js"]},
    {"title": "Game Developer", "company": "Funverse", "location": "Seattle", "skills": ["Unity", "C#", "Game Design"]},
    {"title": "Teacher", "company": "EduWorld", "location": "Dallas", "skills": ["Lesson Planning", "Assessment", "Classroom Management"]},
    {"title": "Research Assistant", "company": "ThinkLab", "location": "Boston", "skills": ["SPSS", "Literature Review", "Data Analysis"]},
    {"title": "Video Editor", "company": "ClipWorks", "location": "Los Angeles", "skills": ["Adobe Premiere", "After Effects", "Color Grading"]},
    {"title": "SEO Specialist", "company": "RankRocket", "location": "Remote", "skills": ["SEO Audit", "Link Building", "Keyword Research"]},
    {"title": "IT Support Technician", "company": "TechHelp", "location": "Charlotte", "skills": ["Windows", "Troubleshooting", "Networking"]},
    {"title": "Animator", "company": "MotionPixel", "location": "San Diego", "skills": ["Maya", "3D Animation", "Rigging"]},
    {"title": "E-commerce Manager", "company": "ShopifyPro", "location": "Remote", "skills": ["Shopify", "Analytics", "Inventory Management"]},
    {"title": "Technical Writer", "company": "DocuTech", "location": "Seattle", "skills": ["Documentation", "Markdown", "Technical Diagrams"]},
    {"title": "AI Researcher", "company": "DeepMinds", "location": "Palo Alto", "skills": ["Reinforcement Learning", "Research Writing", "Python"]},
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
            "title": "The Complete SQL Bootcamp",
            "platform": "Udemy",
            "link": "https://udemy.com/sql-bootcamp"
        },
        {
            "title": "Databases and SQL for Data Science",
            "platform": "Coursera",
            "link": "https://coursera.org/sql"
        }
    ],
    "Machine Learning": [
        {
            "title": "Machine Learning by Andrew Ng",
            "platform": "Coursera",
            "link": "https://coursera.org/ml"
        },
        {
            "title": "Python for Machine Learning",
            "platform": "Udemy",
            "link": "https://udemy.com/ml-python"
        }
    ],
    "React": [
        {
            "title": "React - The Complete Guide",
            "platform": "Udemy",
            "link": "https://udemy.com/react-guide"
        },
        {
            "title": "Modern React with Redux",
            "platform": "Udemy",
            "link": "https://udemy.com/react-redux"
        }
    ],
    "JavaScript": [
        {
            "title": "JavaScript: Understanding the Weird Parts",
            "platform": "Udemy",
            "link": "https://udemy.com/js-weird"
        },
        {
            "title": "JavaScript for Beginners",
            "platform": "Coursera",
            "link": "https://coursera.org/js"
        }
    ],
    "HTML": [
        {
            "title": "HTML Fundamentals",
            "platform": "Coursera",
            "link": "https://coursera.org/html"
        },
        {
            "title": "Build Responsive Websites with HTML",
            "platform": "LinkedIn Learning",
            "link": "https://linkedin.com/learning/html"
        }
    ],
    "CSS": [
        {
            "title": "CSS - The Complete Guide",
            "platform": "Udemy",
            "link": "https://udemy.com/css-complete"
        },
        {
            "title": "Advanced Styling with CSS",
            "platform": "Coursera",
            "link": "https://coursera.org/css"
        }
    ],
    "Data Structures": [
        {
            "title": "Master the Coding Interview: Data Structures + Algorithms",
            "platform": "Udemy",
            "link": "https://udemy.com/ds-algo"
        },
        {
            "title": "Data Structures and Algorithms Specialization",
            "platform": "Coursera",
            "link": "https://coursera.org/dsa"
        }
    ],
    "Statistics": [
        {
            "title": "Intro to Statistics",
            "platform": "Udacity",
            "link": "https://udacity.com/statistics"
        },
        {
            "title": "Basic Statistics",
            "platform": "Coursera",
            "link": "https://coursera.org/statistics"
        }
    ],
    "Excel": [
        {
            "title": "Excel Skills for Business",
            "platform": "Coursera",
            "link": "https://coursera.org/excel"
        },
        {
            "title": "Microsoft Excel - Excel from Beginner to Advanced",
            "platform": "Udemy",
            "link": "https://udemy.com/excel"
        }
    ],
    "Power BI": [
        {
            "title": "Getting Started with Power BI",
            "platform": "Coursera",
            "link": "https://coursera.org/powerbi"
        },
        {
            "title": "Microsoft Power BI - A Complete Introduction",
            "platform": "Udemy",
            "link": "https://udemy.com/powerbi"
        }
    ],
    "Pandas": [
        {
            "title": "Data Analysis with Pandas and Python",
            "platform": "Udemy",
            "link": "https://udemy.com/pandas"
        },
        {
            "title": "Pandas for Data Analysis in Python",
            "platform": "Coursera",
            "link": "https://coursera.org/pandas"
        }
    ],
    "Git": [
        {
            "title": "Git and GitHub for Beginners",
            "platform": "Udemy",
            "link": "https://udemy.com/git-github"
        },
        {
            "title": "Version Control with Git",
            "platform": "Coursera",
            "link": "https://coursera.org/git"
        }
    ],
    "Linux": [
        {
            "title": "Linux Command Line Basics",
            "platform": "Coursera",
            "link": "https://coursera.org/linux"
        },
        {
            "title": "Linux for Beginners",
            "platform": "Udemy",
            "link": "https://udemy.com/linux"
        }
    ],
    "AWS": [
        {
            "title": "AWS Certified Solutions Architect – Associate",
            "platform": "Udemy",
            "link": "https://udemy.com/aws"
        },
        {
            "title": "AWS Fundamentals",
            "platform": "Coursera",
            "link": "https://coursera.org/aws"
        }
    ],
    "Docker": [
        {
            "title": "Docker Mastery",
            "platform": "Udemy",
            "link": "https://udemy.com/docker"
        },
        {
            "title": "Getting Started with Docker",
            "platform": "Pluralsight",
            "link": "https://pluralsight.com/docker"
        }
    ],
    "Kubernetes": [
        {
            "title": "Learn Kubernetes",
            "platform": "Udemy",
            "link": "https://udemy.com/kubernetes"
        },
        {
            "title": "Architecting with Kubernetes",
            "platform": "Coursera",
            "link": "https://coursera.org/kubernetes"
        }
    ],
    "TensorFlow": [
        {
            "title": "Introduction to TensorFlow",
            "platform": "Coursera",
            "link": "https://coursera.org/tensorflow"
        },
        {
            "title": "TensorFlow Developer Certificate in 2024",
            "platform": "Udemy",
            "link": "https://udemy.com/tensorflow"
        }
    ],
    "PyTorch": [
        {
            "title": "Deep Learning with PyTorch",
            "platform": "Coursera",
            "link": "https://coursera.org/pytorch"
        },
        {
            "title": "PyTorch for Deep Learning",
            "platform": "Udemy",
            "link": "https://udemy.com/pytorch"
        }
    ],
    "NLP": [
        {
            "title": "Natural Language Processing with Classification and Vector Spaces",
            "platform": "Coursera",
            "link": "https://coursera.org/nlp"
        },
        {
            "title": "NLP with Python for Machine Learning",
            "platform": "Udemy",
            "link": "https://udemy.com/nlp"
        }
    ],
    "Flutter": [
        {
            "title": "Flutter & Dart - The Complete Guide",
            "platform": "Udemy",
            "link": "https://udemy.com/flutter"
        },
        {
            "title": "Build Native Mobile Apps with Flutter",
            "platform": "Coursera",
            "link": "https://coursera.org/flutter"
        }
    ],
    "React Native": [
        {
            "title": "React Native - The Practical Guide",
            "platform": "Udemy",
            "link": "https://udemy.com/react-native"
        },
        {
            "title": "Multiplatform Mobile App Development with React Native",
            "platform": "Coursera",
            "link": "https://coursera.org/react-native"
        }
    ],
    "Java": [
        {
            "title": "Java Programming Masterclass",
            "platform": "Udemy",
            "link": "https://udemy.com/java"
        },
        {
            "title": "Java for Beginners",
            "platform": "Coursera",
            "link": "https://coursera.org/java"
        }
    ],
    "C++": [
        {
            "title": "Beginning C++ Programming",
            "platform": "Udemy",
            "link": "https://udemy.com/cplusplus"
        },
        {
            "title": "C++ for Programmers",
            "platform": "Coursera",
            "link": "https://coursera.org/cplusplus"
        }
    ],
    "Node.js": [
        {
            "title": "The Complete Node.js Developer Course",
            "platform": "Udemy",
            "link": "https://udemy.com/nodejs"
        },
        {
            "title": "Server-side Development with Node.js",
            "platform": "Coursera",
            "link": "https://coursera.org/nodejs"
        }
    ],
    "MongoDB": [
        {
            "title": "MongoDB for Beginners",
            "platform": "Udemy",
            "link": "https://udemy.com/mongodb"
        },
        {
            "title": "MongoDB Basics",
            "platform": "MongoDB University",
            "link": "https://university.mongodb.com"
        }
    ],
    "Figma": [
        {
            "title": "Learn Figma - UI/UX Design",
            "platform": "Udemy",
            "link": "https://udemy.com/figma"
        },
        {
            "title": "UI/UX Design with Figma",
            "platform": "Coursera",
            "link": "https://coursera.org/figma"
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
