import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from pathlib import Path

try:
    import streamlit as st
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()


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


model = ChatAnthropic(model="claude-sonnet-4-5")

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
    prompt = job_prompt_template.format(job_posting=job_posting)
    structured_llm = model.with_structured_output(Result)
    try:
        return structured_llm.invoke(prompt)
    except Exception as e:
        print(f"Job parsing error: {e}")
        return None

def get_gap_analysis(resume_text: str, job: Result) -> GapAnalysis | None:
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


if __name__ == "__main__":
    RESUME_PATH = "Michael Chung Resume.docx"

    resume_text = load_resume(RESUME_PATH)
    print("Resume loaded.\n")

    job_posting = """
    Job description
    Senior Associate, Data Scientist
    
    Data is at the center of everything we do. As a startup, we disrupted the credit card industry by individually personalizing every credit card offer using statistical modeling and the relational database, cutting edge technology in 1988! Fast-forward a few years, and this little innovation and our passion for data has skyrocketed us to a Fortune 200 company and a leader in the world of data-driven decision-making.
    
    As a Data Scientist at Capital One, you’ll be part of a team that’s leading the next wave of disruption at a whole new scale, using the latest in computing and machine learning technologies and operating across billions of customer records to unlock the big opportunities that help everyday people save money, time and agony in their financial lives.
    
    Team Description
    
    Capital One’s Commercial Bank Team has a $100B+ loan portfolio that has grown organically and via acquisitions, covering Corporate Banking, CRE, and NBFI lending. And our team provides analytical tools and models to forecast bank volume, revenue and expense. On this team, you’ll get an opportunity to solve a diverse set of problems, with a diverse set of tools. This role would have exposure to both model implementation and model development. It’s a growing team, full of exciting opportunities to solve a range of complex problems.
    
    Role Description
    
    In this role, you will:
    • Partner with a cross-functional team of data scientists, software engineers, and product managers to deliver a product customers love
    • Leverage a broad stack of technologies — Python, Conda, AWS, H2O, Spark, and more — to reveal the insights hidden within huge volumes of numeric and textual data
    • Build machine learning models through all phases of development, from design through training, evaluation, validation, and implementation
    • Flex your interpersonal skills to translate the complexity of your work into tangible business goals
    
    The Ideal Candidate is:
    • Innovative. You continually research and evaluate emerging technologies. You stay current on published state-of-the-art methods, technologies, and applications and seek out opportunities to apply them.
    • Creative. You thrive on bringing definition to big, undefined problems. You love asking questions and pushing hard to find answers. You’re not afraid to share a new idea.
    • Technical. You’re comfortable with open-source languages and are passionate about developing further. You have hands-on experience developing data science solutions using open-source tools and cloud computing platforms.
    • Statistically-minded. You’ve built models, validated them, and backtested them. You know how to interpret a confusion matrix or a ROC curve. You have experience with clustering, classification, sentiment analysis, time series, and deep learning.
    • A data guru. “Big data” doesn’t faze you. You have the skills to retrieve, combine, and analyze data from a variety of sources and structures. You know understanding the data is often the key to great data science.
    
    Basic Qualifications:
    • Currently has, or is in the process of obtaining one of the following with an expectation that the required degree will be obtained on or before the scheduled start date:
    • A Bachelor's Degree in a quantitative field (Statistics, Economics, Operations Research, Analytics, Mathematics, Computer Science, or a related quantitative field) plus 2 years of experience performing data analytics
    • A Master's Degree in a quantitative field (Statistics, Economics, Operations Research, Analytics, Mathematics, Computer Science, or a related quantitative field) or an MBA with a quantitative concentration
    
    Preferred Qualifications:
    • Master’s Degree in “STEM” field (Science, Technology, Engineering, or Mathematics), or PhD in “STEM” field (Science, Technology, Engineering, or Mathematics)
    • Experience working with AWS
    • At least 2 years’ experience in Python, Scala, or R
    • At least 2 years’ experience with machine learning
    • At least 2 years’ experience with SQL
    • Experience with AI-assisted development is a plus.
    • Financial knowledge is a plus
    
    Capital One will consider sponsoring a new qualified applicant for employment authorization for this position.
    
    The minimum and maximum full-time annual salaries for this role are listed below, by location. Please note that this salary information is solely for candidates hired to perform work within one of these locations, and refers to the amount Capital One is willing to pay at the time of this posting. Salaries for part-time roles will be prorated based upon the agreed upon number of hours to be regularly worked.
    
    McLean, VA: $135,600 - $154,800 for Sr Assoc, Data Science
    
    New York, NY: $148,000 - $168,900 for Sr Assoc, Data Science
    
    Candidates hired to work in other locations will be subject to the pay range associated with that location, and the actual annualized salary amount offered to any candidate at the time of hire will be reflected solely in the candidate’s offer letter.
    
    This role is also eligible to earn performance based incentive compensation, which may include cash bonus(es) and/or long term incentives (LTI). Incentives could be discretionary or non discretionary depending on the plan.
    
    Capital One offers a comprehensive, competitive, and inclusive set of health, financial and other benefits that support your total well-being. Learn more at the Capital One Careers website. Eligibility varies based on full or part-time status, exempt or non-exempt status, and management level.
    
    This role is expected to accept applications for a minimum of 5 business days.
    
    No agencies please. Capital One is an equal opportunity employer (EOE, including disability/vet) committed to non-discrimination in compliance with applicable federal, state, and local laws. Capital One promotes a drug-free workplace. Capital One will consider for employment qualified applicants with a criminal history in a manner consistent with the requirements of applicable laws regarding criminal background inquiries, including, to the extent applicable, Article 23-A of the New York Correction Law; San Francisco, California Police Code Article 49, Sections 4901-4920; New York City’s Fair Chance Act; Philadelphia’s Fair Criminal Records Screening Act; and other applicable federal, state, and local laws and regulations regarding criminal background inquiries.
    
    If you have visited our website in search of information on employment opportunities or to apply for a position, and you require an accommodation, please contact Capital One Recruiting at 1-800-304-9102 or via email at RecruitingAccommodation@capitalone.com. All information you provide will be kept confidential and will be used only to the extent required to provide needed reasonable accommodations.
    
    For technical support or questions about Capital One's recruiting process, please send an email to Careers@capitalone.com
    
    Capital One does not provide, endorse nor guarantee and is not liable for third-party products, services, educational tools or other information available through this site.
    
    Capital One Financial is made up of several different entities. Please note that any position posted in Canada is for Capital One Canada, any position posted in the United Kingdom is for Capital One Europe and any position posted in the Philippines is for Capital One Philippines Service Corp. (COPSSC). 
    """

    job = get_job_result(job_posting)
    if not job:
        print("Failed to parse job posting.")
        exit()

    print(f"Role: {job.job_title}")
    print(f"Summary: {job.job_summary}\n")

    gap = get_gap_analysis(resume_text, job)
    if gap:
        print("GAP ANALYSIS")
        print(f"\nRecommendation: {gap.recommendation}")
        print(f"\nOverall Fit: {gap.overall_fit}")
        print(f"\nStrong Matches:\n" + "\n".join(f"  ✓ {s}" for s in gap.strong_matches))
        print(f"\nPartial Matches:\n" + "\n".join(f"  ~ {s}" for s in gap.partial_matches))
        print(f"\nGaps:\n" + "\n".join(f"  ✗ {s}" for s in gap.gaps))
