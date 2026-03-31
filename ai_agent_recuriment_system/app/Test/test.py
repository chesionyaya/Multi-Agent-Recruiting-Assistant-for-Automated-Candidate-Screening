from app.agents.cv_parsing_agent import CV_parsing_agent
from app.agents.jd_understanding_agent import Jd_understanding_agent

# job_text = """
# We are looking for an NLP Engineer Intern.
# Required: Python, NLP, Transformers, PyTorch.
# Preferred: RAG, FastAPI, Docker.
# At least 1 year of experience in machine learning projects.
# Bachelor's or Master's in Computer Science, AI, or Data Science.
# """

candidate_cv =  """
    Ceqin Lan
Barcelona, Spain
Email: ceqinlan@example.com
Phone: +34 600 123 456
LinkedIn: linkedin.com/in/ceqinlan
GitHub: github.com/ceqinlan

PROFILE
MSc student in Intelligent Interactive Systems with a background in Computer Science.
Interested in NLP, LLM applications, data science, and AI engineering.
Hands-on experience in building end-to-end data pipelines, sentiment analysis systems, and retrieval-augmented generation applications.

EDUCATION
MSc in Intelligent Interactive Systems
University Pompeu Fabra, Barcelona
2024 – Present

BSc in Computer Science
University of Debrecen
2019 – 2023

SKILLS
Python, SQL, Pandas, NumPy, Scikit-learn, PyTorch, Transformers, FastAPI, Docker, Git, FAISS, NetworkX

WORK EXPERIENCE
Data Science Intern
Huaxin Trust
Jun 2023 – Sep 2023
- Processed large-scale customer data for profiling and predictive analysis.
- Performed data cleaning, feature engineering, and model training.
- Built classification models to identify potential customer segments.
- Evaluated model performance and improved prediction quality through iterative tuning.

PROJECTS
Financial Sentiment Analysis and RAG System
- Collected YouTube comments related to Apple AI products and combined them with stock market data.
- Applied VADER, TextBlob, and BERT-based sentiment analysis to measure public reaction.
- Built a FAISS-based retrieval system for question answering over monthly sentiment-stock summaries.

Recruitment AI Screening Agent
- Designed an agent-based pipeline for job description understanding, candidate parsing, matching, and explanation generation.
- Used Pydantic schemas to structure job and candidate profiles.
- Implemented rule-based skill extraction and profile matching for candidate screening.

LANGUAGES
Chinese (Native), English (Fluent)
    """



cv_agent = CV_parsing_agent()
result = cv_agent.run(candidate_cv)
print(result.model_dump())