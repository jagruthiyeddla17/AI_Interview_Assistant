import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
import os

load_dotenv()

# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Page Title
st.set_page_config(page_title="AI Interview Preparation Assistant")

st.title("AI Interview Preparation Assistant")
uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

resume_text = ""

if uploaded_file:

    reader = PdfReader(uploaded_file)

    for page in reader.pages:
        text = page.extract_text()

        if text:
            resume_text += text

    st.success("Resume uploaded successfully!")
    
# Check API Key
if not api_key:
    st.error("Groq API Key Not Found!")
    st.info("Add GROQ_API_KEY to your .env file")
    st.stop()

st.success("Groq API Key Loaded Successfully")

# Create Groq client
client = Groq(api_key=api_key)
if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

# User Input
role = st.text_input(
    "Enter Job Role",
    placeholder="Example: Data Analyst, Software Engineer, Data Scientist"
)

# Generate Questions Button
if st.button("Generate Questions"):

    if not role:
        st.warning("Please enter a job role.")
        st.stop()

    try:

        prompt = f"""
You are an interviewer.

Candidate Resume:

{resume_text}

Job Role:

{role}

Generate:

1. 5 Technical Questions based on the resume
2. 3 HR Questions
3. 2 Resume-Based Questions

Questions should be relevant to the candidate's skills,
projects, internship experience, and job role.

Format:

## Technical Questions
1.
2.
3.
4.
5.

## HR Questions
1.
2.
3.

## Situational Questions
1.
2.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )

        questions = response.choices[0].message.content

        st.subheader(f"Interview Questions for {role}")
        st.write(questions)

    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.header("Answer Evaluation")

question = st.text_area(
    "Interview Question",
    height=100
)

answer = st.text_area(
    "Your Answer",
    height=200
)

if st.button("Evaluate Answer"):

    if not question or not answer:
        st.warning("Please enter both question and answer.")
    else:

        evaluation_prompt = f"""
You are a senior interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer.

Provide:

1. Score out of 10
2. Strengths
3. Weaknesses
4. Improved Answer
5. Interviewer's Feedback

Be professional and constructive.
"""

        evaluation = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": evaluation_prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )

        st.subheader("Evaluation Result")

        st.write(
            evaluation.choices[0].message.content
        )
        
        if st.button("Start Mock Interview"):

            st.session_state.questions = [
                "Tell me about yourself.",
                "What is SQL JOIN?",
                "Explain a project from your resume."
            ]

st.session_state.current_question = 0
st.session_state.answers = []
st.caption("Powered by Groq + Llama 3.3 70B")
st.write(resume_text[:500])  
