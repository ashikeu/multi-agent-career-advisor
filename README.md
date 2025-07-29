# Multi-Agent Career Advisor – “CareerMate”

Build a multi-agent system called CareerMate that helps users explore and plan career paths. The system includes a Conversation Agent that handles general career queries and routes requests to three Specialist Agents:

Skill Gap Agent


Job Finder Agent


Course Recommender Agent


Each agent uses specific tools and datasets (real or dummy), and works together to guide the user through discovering job opportunities, identifying skill gaps, and learning the necessary skills.


## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```
2. Install the Agents SDK
pip install openai-agents 

3. Create the venv:
python -m venv venv

4. Activate Virtual Environment

venv\Scripts\activate

5. Create a `.env` file with your OpenAI API key:

```
BASE_URL="https://models.github.ai/inference/v1"
API_KEY=
MODEL_NAME="openai/gpt-4.1-nano"

```

## Running the Examples

```bash
python carrear_mate.py
```

## Running the Streamlit
Install streamlit

pip install streamlit

```bash
streamlit run app.py
```


