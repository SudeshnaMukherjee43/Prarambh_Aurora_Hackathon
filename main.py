import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

career_data = pd.read_csv("careers.csv")

# ------------------ Custom Styling ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f5f7fa;
    }

    .block-container {
        padding: clamp(1rem, 2vw, 2rem);
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.06);
        max-width: 1200px;
        margin: 0 auto;
    }

    h1 {
        color: #1f2937;
        font-size: clamp(1.75rem, 3vw, 2.5rem);
        line-height: 1.2;
    }

    h2, h3, h4 {
        color: #1f2937;
        font-size: clamp(1.25rem, 2vw, 1.75rem);
    }

    .stButton>button {
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        border: none;
        padding: clamp(0.5em, 1vw, 0.6em) clamp(1em, 2vw, 1.2em);
        border-radius: 8px;
        transition: background-color 0.3s ease;
        width: 100%;
        max-width: 300px;
    }

    .stButton>button:hover {
        background-color: #1e40af;
    }

    .section-divider {
        margin: clamp(20px, 4vw, 40px) 0 clamp(10px, 2vw, 20px) 0;
        border-bottom: 1px solid #e5e7eb;
    }

    .stTextInput>div>div>input, 
    .stTextArea>div>textarea, 
    .stFileUploader>div>div {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        width: 100%;
        max-width: 100%;
    }

    .stMultiSelect>div>div {
        border-radius: 8px;
        background-color: #ffffff;
        max-width: 100%;
    }

    /* Responsive text sizing */
    .stMarkdown {
        font-size: clamp(14px, 1.5vw, 16px);
    }

    /* Responsive padding for mobile */
    @media screen and (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }
        
        .stTextInput>div>div>input, 
        .stTextArea>div>textarea {
            font-size: 16px; /* Prevents zoom on mobile */
        }
    }

    /* File uploader responsive styling */
    .stFileUploader>div {
        width: 100%;
        max-width: 100%;
    }

    /* Make multiselect dropdown responsive */
    .stMultiSelect>div {
        max-width: 100%;
    }

    /* Improve text readability on small screens */
    .stText {
        word-wrap: break-word;
        max-width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ App UI ------------------
st.title("🎯 AI Career Counselor")
st.subheader("Your Personalized Career Assistant")

name = st.text_input("Your Name")
email = st.text_input("Email Address")

if name and email:
    st.success(f"Welcome, {name}. Let's discover your future together.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.header("📄 Resume Analysis")

    resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    extracted_resume_skills = []

    if resume_file:
        from docx import Document
        import fitz
        def extract_resume_text(file):
            if file.type == "application/pdf":
                text = ""
                pdf = fitz.open(stream=file.read(), filetype="pdf")
                for page in pdf:
                    text += page.get_text()
                return text
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(file)
                return "\n".join([para.text for para in doc.paragraphs])
            return ""

        with st.spinner("Analyzing resume..."):
            resume_text = extract_resume_text(resume_file)

            def extract_skills_with_openai(resume_text):
                prompt = (
                    "You are an expert resume analyzer. Extract only the relevant skills "
                    "from the following resume text:\n\n" + resume_text
                )
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a resume analysis assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=200,
                    temperature=0.5,
                )
                return response.choices[0].message.content.strip()

            extracted = extract_skills_with_openai(resume_text)
            st.success("Skills extracted from your resume:")
            st.text(extracted)
            extracted_resume_skills = [s.strip() for s in extracted.split(',') if s.strip()]

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.header("🧠 Skill Selection")

    all_skills = sorted(set(
        skill.strip() for sublist in career_data['required_skills'].str.split(',')
        for skill in sublist
    ))

    selected_skills = st.multiselect("Choose from available skills:", all_skills)

    manual_input = st.text_input("Or enter your skills manually (comma-separated):")
    manual_skills = [s.strip() for s in manual_input.split(',') if s.strip()]

    combined_skills = list(set(selected_skills + manual_skills + extracted_resume_skills))

    if combined_skills:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.header("💼 Career Recommendations")

        def recommend_careers_openai(skills):
            prompt = (
                "You are a helpful career counselor. Based on these skills: "
                + ", ".join(skills)
                + ", suggest 5 suitable career paths with a short description for each."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful career counselor."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=700,
                temperature=0.7,
            )
            return response.choices[0].message.content

        recommendations_text = recommend_careers_openai(combined_skills)
        st.markdown("#### Suggested Career Paths:")
        st.text(recommendations_text)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.header("📚 Learning Resources")

        chosen_career = st.text_input("Enter a career you're curious about:")

        if st.button("Get Resources"):
            if chosen_career:
                def fetch_learning_resources(career_name):
                    prompt = (
                        f"For someone interested in becoming a {career_name}, recommend:\n"
                        f"1. 2 Indian YouTube videos\n"
                        f"2. 2 International YouTube videos\n"
                        f"3. 2-3 relevant websites\n"
                        f"4. Free/Paid Online Courses\n\nPlease include clickable links."
                    )
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a learning advisor."},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=700,
                        temperature=0.6,
                    )
                    return response.choices[0].message.content.strip()

                with st.spinner("Gathering curated resources..."):
                    resources = fetch_learning_resources(chosen_career)
                    st.markdown("##### Curated Resources:")
                    st.markdown(resources, unsafe_allow_html=True)
            else:
                st.warning("Please enter a career name first.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.header("💬 Feedback")

    comment = st.text_area("Your thoughts, suggestions, or questions:")
    if st.button("Submit Feedback"):
        if comment.strip():
            with open("comments.txt", "a") as f:
                f.write(f"Name: {name}, Email: {email}, Comment: {comment}\n")
            st.success("Thank you! We appreciate your input.")
        else:
            st.warning("Comment cannot be empty.")

else:
    st.info("Please enter your name and email to begin.")