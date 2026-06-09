# Job Fit Analyzer

An AI-powered tool that analyzes your resume against job postings and identifies strengths, gaps, and partial matches with a hiring recommendation.

## Tech Stack
Python · LangChain · Claude API · Streamlit

## Live Demo
[job-fit-analyzer-me.streamlit.app](https://job-fit-analyzer-me.streamlit.app)


![Quick Look](https://github.com/user-attachments/assets/87043e21-db16-497d-914f-0f0eb0618e9c)
*Parsed job details: title, skills, salary, and work arrangement*

![Results](https://github.com/user-attachments/assets/1fa7910e-dfd0-4eb4-ae66-bf25d9b503e0)
*Gap analysis: strong matches, partial matches, and gaps against your resume*

## Run Locally
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Anthropic API key to `.env`: `ANTHROPIC_API_KEY=your_key_here`
4. Run: `python -m streamlit run app.py`
