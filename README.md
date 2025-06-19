# 🧠 ATS Resume Evaluator

An intelligent Streamlit-based application that mimics an ATS (Applicant Tracking System) to evaluate resumes against job descriptions using the **Azure OpenAI GPT-4o-mini** model.

This tool calculates match percentages, identifies missing technical skills, and helps recruiters or candidates understand resume-job fit in real time.

---

## 🚀 Features

- 🔍 Extracts text from uploaded **PDF resumes**
- 🤖 Uses **GPT-4o-mini** (via Azure) to analyze resumes
- 📊 Calculates **match percentage**
- 🧠 Detects **missing technical skills**
- 📌 Supports **multiple resume uploads**
- ❓ Accepts **custom questions** about job fit
- 🏆 Identifies the **best fit** among multiple candidates

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/)
- [Azure OpenAI (GPT-4o-mini)](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/shettyrohit0810/ats-resume-evaluator.git
cd ats-resume-evaluator
