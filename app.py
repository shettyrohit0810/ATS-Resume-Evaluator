#ats system

import os

import openai

import streamlit as st

import PyPDF2 as pdf

from dotenv import load_dotenv

import json

import re

 

# Load environment variables for the API key

load_dotenv()

 

# Configure Azure OpenAI API

openai.api_type = "azure"

openai.api_base = "https://openai-models-for-poc.openai.azure.com/"  # Your updated Azure OpenAI API base

openai.api_key = os.getenv("AZURE_API_KEY")  # Store your API key in .env

openai.api_version = "2024-02-15-preview"

 

# Function to get a response from Azure's GPT-4o-mini model

def get_gpt35_response(input_text):

    try:

        response = openai.ChatCompletion.create(

            engine="gpt-4o-mini",  # Replace with your updated engine deployment name

            messages=[

                {"role": "user", "content": input_text}

            ],

            max_tokens=1000,

            temperature=0.7

        )

        return response['choices'][0]['message']['content'].strip()

    except Exception as e:

        return f"Error generating response: {e}"

 

# Function to extract text from PDF files

def input_pdf_text(uploaded_file):

    reader = pdf.PdfReader(uploaded_file)

    text = ""

    for page in range(len(reader.pages)):

        text += reader.pages[page].extract_text()

    return text

 

# Prompt templates for different types of evaluation

input_prompt1 = """

You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.

Please share your professional evaluation on whether the candidate's profile aligns with the role.

Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements, and mention any missing important technical skills.

Resume: {text}

Description: {jd}

"""

 

input_prompt2 = """
You are an experienced ATS (Application Tracking System) with a deep understanding of the tech field. 
Your task is to evaluate the resume based on the given job description.
Identify only the **critical technical skills** (e.g., programming languages, tools, technologies) that are missing in the resume compared to the job description.
Resume: {text}
Description: {jd}
"""



 

input_prompt_question = """

You are a highly capable AI assistant with a deep understanding of resumes and job matching. Given the following resume and job description,

please answer the user's question:

Resume: {text}

Job Description: {jd}

Question: {question}

"""

 

input_prompt_best_fit = """

You are an experienced AI assistant specialized in job matching and evaluating resumes. Based on the following resumes and job description,

evaluate which candidate's experience is the best fit for the job. Provide a detailed comparison of the top candidates and explain why they are suitable.

Resumes: {resumes}

Job Description: {jd}

"""

 

# Streamlit App UI

st.title("ATS System for Candidate Evaluation")

st.header("Applicant Tracking System (ATS)")

 

# Input for job description

jd = st.text_area("Paste the Job Description")

 

# Resume upload (multiple PDFs allowed)

uploaded_files = st.file_uploader("Upload Candidate Resumes", type="pdf", accept_multiple_files=True, help="Please upload the PDF files")

 

# Optional question input for specific evaluation

ask_question = st.text_input("Ask a question about the resumes or job description")

 

# Buttons to trigger different functionalities

submit_analysis = st.button("Tell Me About the Resumes")

submit_percentage = st.button("Percentage Match")

submit_question = st.button("Evaluate Candidates Based on Questions")

submit_best_fit = st.button("Who is the Best Fit?")


# Function to calculate keyword match based on GPT-driven keyword extraction
def calculate_keyword_match(resume_text, jd_text):
    # Create the prompt to get keywords from the resume and job description using GPT
    prompt = """
    You are an experienced AI assistant. Based on the following job description and resume, identify the most important technical keywords (e.g., programming languages, tools, technologies) in each text.

    Job Description: {jd}

    Resume: {resume}

    Please return a list of important technical keywords identified from the job description and the resume.
    """

    formatted_prompt = prompt.format(jd=jd_text, resume=resume_text)
    response = get_gpt35_response(formatted_prompt)
    
    # Process the response to extract keywords from GPT's output
    keywords = response.strip().split("\n")  # Each keyword will be assumed to be on a new line
    keywords = [keyword.strip() for keyword in keywords if keyword.strip()]
    
    # Split the keywords into those from JD and those from the resume (simply by counting overlap)
    jd_keywords = set(re.findall(r'\b\w+\b', jd_text.lower()))
    resume_keywords = set(re.findall(r'\b\w+\b', resume_text.lower()))

    # Match count based on keyword overlap
    match_count = len(jd_keywords & resume_keywords)
    
    if len(jd_keywords) == 0:
        return 0  # Avoid division by zero
    
    # Calculate percentage match
    percentage_match = (match_count / len(jd_keywords)) * 100
    
    # Give weight to the match for important keywords (from JD)
    weighted_match = 0
    for keyword in jd_keywords:
        if keyword in resume_keywords:
            weighted_match += 2  # Increase weight for each match

    # Apply a scaling factor to the weighted match to better differentiate candidates
    weighted_percentage = (weighted_match / len(jd_keywords)) * 100

    # Adjust the match score based on missing critical skills
    if weighted_percentage < 50:
        weighted_percentage = max(weighted_percentage, 90)  # Ensure a minimum 60% score if critical skills are missing

    # Final score will be a blend of both
    final_percentage = (weighted_percentage + percentage_match) / 2  # Average the weighted and raw match percentage

    return round(final_percentage, 2)


# Function to identify missing keywords, focusing on technical skills

def find_missing_keywords(resume_text, jd_text):

    jd_keywords = set(re.findall(r'\b\w+\b', jd_text.lower()))

    resume_keywords = set(re.findall(r'\b\w+\b', resume_text.lower()))

    missing_keywords = jd_keywords - resume_keywords

    return list(missing_keywords)

 

# Function to calculate relevance score based on the user's question

def calculate_relevance_score(response, question):

    if not response or not question:

        return 0

    relevant_keywords = question.split()

    score = sum(1 for keyword in relevant_keywords if keyword.lower() in response.lower())

    return score * 10  

 
# Percentage Match for each resume along with missing technical keywords (Keyword analysis only)
if submit_percentage and uploaded_files:
    resume_rankings = []  # List to store rankings based on keyword match
    
    for uploaded_file in uploaded_files:
        # Extract text from the resume
        text = input_pdf_text(uploaded_file)

        # Create the prompt and get response from GPT model
        formatted_prompt = input_prompt2.format(text=text, jd=jd)
        response = get_gpt35_response(formatted_prompt)

        # Process the response to get the missing technical skills (keywords)
        missing_keywords = response.strip().split("\n")  # Assuming each missing skill is on a new line
        missing_keywords = [keyword.strip() for keyword in missing_keywords if keyword.strip()]

        # Calculate the match percentage using GPT-extracted keywords
        percentage_match = calculate_keyword_match(text, jd)

        # Append results to the rankings list
        resume_rankings.append((uploaded_file.name, percentage_match, missing_keywords))

    # Display the rankings based on missing technical keywords
    st.subheader("Candidate Rankings Based on Missing Technical Keywords:")

    for rank, (resume_name, score, missing_keywords) in enumerate(resume_rankings, 1):
        st.write(f"{rank}. **{resume_name}** - Match Percentage: {score}%")
        if missing_keywords:
            st.write(f"  **Missing Keywords**:")
            for keyword in missing_keywords:
                st.write(f"  - {keyword}")
        else:
            st.write(f"  **Missing Keywords**: None")
            
            
# Evaluate which candidate is the best fit overall

if submit_best_fit and uploaded_files:

    resumes_texts = []

   

    for uploaded_file in uploaded_files:

        resume_text = input_pdf_text(uploaded_file)

        resumes_texts.append(f"{uploaded_file.name}: {resume_text}")

 

    formatted_prompt = input_prompt_best_fit.format(resumes=" ".join(resumes_texts), jd=jd)

    response = get_gpt35_response(formatted_prompt)

 

    # Check if response is structured properly

    st.subheader("Best Fit Candidate(s) Evaluation:")

    st.write(response)
