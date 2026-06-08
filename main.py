from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from pathlib import Path
import os

class SalaryRange(BaseModel):
    min_salary: int = Field(description="minimum salary")
    max_salary: int = Field(description="maximum salary")

class Result(BaseModel):
    job_title: str = Field(description="title of the role")
    job_summary: str = Field(description='brief summary of the role')
    required_skills: list[str] = Field(description='Skills required for the role')
    preferred_skills: list[str] = Field(default=None, description='Skills preferred for the role, optional')
    salary_range: SalaryRange = Field(default=None, description='minimum and maximum salary listed, optional')
    work_arrangement: str = Field(description='Expected work setting: on-site/remote/hybrid/etc')
    experience_req: str = Field(default=None, description='years of experience required, optional')
    responsibilities: list[str] = Field(description='Key tasks and responsibilities expected for the role')
    qualifications: list[str] = Field(description='key requirements needed for the role such as education, certifications, clearance, etc.')
    benefits: list[str] = Field(default=None, description='benefits obtained from the role, optional')

class GapAnalysis(BaseModel):
    strong_matches: list[str] = Field(description="Skills/qualifications from the job that the candidate clearly has")
    gaps: list[str] = Field(description="Skills/qualifications required or preferred that the candidate is missing or weak in")
    partial_matches: list[str] = Field(description="Areas where the candidate has some relevant experience but not a full match")
    overall_fit: str = Field(description="Brief overall assessment of candidate fit for the role (2-3 sentences)")
    recommendation: str = Field(description="Whether to apply: 'Strong Apply', 'Apply w/ Caveats', or 'Skip'")

def load_resume(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Resume not found: {path}")
    suffix = p.suffix.lower()
    if suffix == ".docx":
        import docx
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    elif suffix == ".pdf":
        import pdfplumber
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .docx or .pdf")

job_prompt_template = PromptTemplate.from_template("""
You are a helpful job searching assistant. Your job is to read a job posting:
{job_posting}
and extract these key attributes:
- job_title, job_summary, required_skills, preferred_skills, salary_range,
  work_arrangement, experience_required, responsibilities, qualifications, benefits

Output as a Pydantic object. Minimize overlap. If no confident answer, state there is no answer.
""")

gap_prompt_template = PromptTemplate.from_template("""
You are a career coach doing a resume-to-job-posting gap analysis.

RESUME:
{resume}

JOB POSTING SUMMARY:
Title: {job_title}
Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Qualifications: {qualifications}
Experience Required: {experience_req}

Analyze the candidate's fit. Identify strong matches, gaps, and partial matches.
Be specific — reference actual skills, tools, and qualifications by name. The output should be 2nd person,
as if you are speaking to the candidate directly.
""")

def get_job_result(job_posting: str) -> Result | None:
    model = ChatAnthropic(model="claude-sonnet-4-5")
    prompt = job_prompt_template.format(job_posting=job_posting)
    structured_llm = model.with_structured_output(Result)
    try:
        return structured_llm.invoke(prompt)
    except Exception as e:
        print(f"Job parsing error: {e}")
        return None

def get_gap_analysis(resume_text: str, job: Result) -> GapAnalysis | None:
    model = ChatAnthropic(model="claude-sonnet-4-5")
    prompt = gap_prompt_template.format(
        resume=resume_text,
        job_title=job.job_title,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills or [],
        qualifications=job.qualifications,
        experience_req=job.experience_req or "Not specified"
    )
    structured_llm = model.with_structured_output(GapAnalysis)
    try:
        return structured_llm.invoke(prompt)
    except Exception as e:
        print(f"Gap analysis error: {e}")
        return None