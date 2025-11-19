import pandas as pd
from typing import List, Dict
from utils.groq_analyzer import analyze_resume
from utils.pdf_handler import extract_text_from_pdf
import re

class JobMatcher:
    """
    Match resume data with job postings and calculate relevance scores.
    """
    def __init__(self, jobs_csv_path: str):
        """
        Initialize matcher with jobs dataset.
        
        Args:
            jobs_csv_path: Path to filtered jobs CSV
        """
        # Load CSV and drop unnamed columns
        self.jobs_df = pd.read_csv(jobs_csv_path)
        
        # Drop all 'Unnamed' columns
        unnamed_cols = [col for col in self.jobs_df.columns if col.startswith('Unnamed')]
        if unnamed_cols:
            self.jobs_df = self.jobs_df.drop(columns=unnamed_cols)
            print(f"🧹 Dropped {len(unnamed_cols)} unnamed columns")
        
        print(f"✅ Loaded {len(self.jobs_df)} jobs")
        print(f"📊 Columns: {list(self.jobs_df.columns)}")
        
        # Your CSV structure: company, category, post_link, job_description, location, date_posted, keywords
        self.col_names = {
            'Job_Title': 'category',  # Using category as job title
            'Job_Description': 'job_description',
            'Company': 'company',
            'Location': 'location',
            'Experience_Level': None  # Not available
        }

    def extract_title_from_description(self, description: str) -> str:
        """
        Extract job title from description if category is missing.
        """
        if pd.isna(description):
            return "Unknown Position"
        
        # Try to find title in first 200 chars
        first_part = str(description)[:200]
        
        # Common patterns: "Position: Title" or "Title - Company" or just first line
        lines = first_part.split('\n')
        if lines:
            return lines[0].strip()[:100]  # First line as title
        
        return "Unknown Position"

    def calculate_skill_match(self, resume_skills: List[str], 
                            job_description: str,
                            job_title: str,
                            job_keywords: str = None) -> float:
        """Calculate skill match score using keywords and description."""
        
        if not resume_skills:
            return 0.0
        
        # Combine ALL text sources (keywords are most important!)
        text_parts = [str(job_description), str(job_title)]
        if job_keywords and not pd.isna(job_keywords):
            text_parts.append(str(job_keywords))
        
        combined_text = " ".join(text_parts).lower()
        
        # Count matching skills
        matched_count = sum(1 for skill in resume_skills if skill.lower() in combined_text)
        
        score = matched_count / len(resume_skills) if resume_skills else 0.0
        
        return score

    def estimate_experience_level(self, job_description: str, job_title: str) -> str:
        """
        Estimate experience level from job description and title.
        """
        if pd.isna(job_description):
            job_description = ""
        if pd.isna(job_title):
            job_title = ""
        
        combined = (str(job_description) + " " + str(job_title)).lower()
        
        # Check for level indicators
        if any(word in combined for word in ['intern', 'internship']):
            return 'Internship'
        elif any(word in combined for word in ['entry level', 'junior', 'graduate', 'associate']):
            return 'Entry level'
        elif any(word in combined for word in ['senior', 'sr.', 'lead', 'principal']):
            return 'Mid-Senior level'
        elif any(word in combined for word in ['director', 'head of', 'vp', 'vice president']):
            return 'Director'
        elif any(word in combined for word in ['chief', 'cto', 'ceo', 'executive']):
            return 'Executive'
        else:
            return 'Mid-Senior level'  # Default

    def calculate_experience_match(self, resume_years: float, job_level: str) -> float:
        """Calculate experience level match."""
        
        if pd.isna(job_level) or job_level == '':
            return 0.5  # Neutral score
        
        # Map levels to year ranges
        level_ranges = {
            'Internship': (0, 1),
            'Entry level': (0, 2),
            'Associate': (1, 3),
            'Mid-Senior level': (3, 8),
            'Director': (8, 15),
            'Executive': (15, 30)
        }
        
        if job_level not in level_ranges:
            return 0.5
        
        min_years, max_years = level_ranges[job_level]
        
        if min_years <= resume_years <= max_years:
            return 1.0
        elif resume_years < min_years:
            gap = min_years - resume_years
            if gap <= 0.5:
                return 0.95
            elif gap <= 1.0:
                return 0.85
            elif gap <= 1.5:
                return 0.70
            elif gap <= 2.0:
                return 0.55
            else:
                return 0.30
        else:
            gap = resume_years - max_years
            if gap <= 1.0:
                return 0.90
            elif gap <= 2.0:
                return 0.75
            elif gap <= 3.0:
                return 0.60
            else:
                return 0.40
    
    def calculate_title_match(self, job_title: str, resume_desired_roles: List[str]) -> float:
        """Check if job title matches desired roles."""
        
        if not resume_desired_roles or pd.isna(job_title):
            return 0.5
        
        job_title = str(job_title).lower()
        
        for desired in resume_desired_roles:
            desired_words = set(desired.lower().split())
            title_words = set(job_title.split())
            common_words = desired_words & title_words
            
            if len(common_words) >= 2:
                return 1.0
            elif len(common_words) == 1:
                return 0.7
        
        return 0.3
    
    def calculate_overall_score(self, resume_data: Dict, job_row: pd.Series) -> Dict:
        """Calculate overall match score."""
        
        job_title = job_row.get('category')
        job_description = job_row.get('job_description')
        
        # If category is empty, try to extract title from description
        if pd.isna(job_title) or job_title == '':
            job_title = self.extract_title_from_description(job_description)
        
        # Estimate experience level from text
        estimated_level = self.estimate_experience_level(job_description, job_title)
        
        skill_score = self.calculate_skill_match(
            resume_data['skills'],
            job_description,
            job_title
        )
        
        exp_score = self.calculate_experience_match(
            resume_data['experience_years'],
            estimated_level
        )
        
        title_score = self.calculate_title_match(
            job_title,
            resume_data.get('desired_roles', [])
        )

        weights = {
            'skills': 0.50,
            'experience': 0.30,
            'title': 0.20
        }
        
        overall = (
            skill_score * weights['skills'] +
            exp_score * weights['experience'] +
            title_score * weights['title']
        )
        
        return {
            'overall': overall,
            'skill_score': skill_score,
            'exp_score': exp_score,
            'title_score': title_score,
            'estimated_level': estimated_level
        }
    
    def finding_matching_jobs(self, resume_data: Dict, top_n: int = 10, min_score: float = 0.3) -> pd.DataFrame:
        """Find top matching jobs."""
        
        experience_years = resume_data.get('experience_years', 0)
        career_level = resume_data.get('career_level', '')
        
        print(f"\n Searching {len(self.jobs_df):,} jobs...")
        print(f" Resume profile:")
        print(f"   - Experience: {experience_years} years")
        print(f"   - Level: {career_level}")
        print(f"   - Skills: {len(resume_data.get('skills', []))} skills")
        
        results = []
        
        print(f"\n Calculating match scores...")
        
        for idx, job in self.jobs_df.iterrows():
            scores = self.calculate_overall_score(resume_data, job)
            
            # Debug first few jobs
            if idx < 5:
                print(f"\n   Job {idx+1}: {str(job.get('category', 'No title'))[:50]}")
                print(f"   Overall: {scores['overall']:.1%} | Skills: {scores['skill_score']:.1%} | Exp: {scores['exp_score']:.1%} | Title: {scores['title_score']:.1%}")
            
            if scores['overall'] >= min_score:
                job_title = job.get('category')
                if pd.isna(job_title) or job_title == '':
                    job_title = self.extract_title_from_description(job.get('job_description'))
                
                results.append({
                    'title': job_title,
                    'company': job.get('company'),
                    'location': job.get('location'),
                    'experience_level': scores['estimated_level'],
                    'description': job.get('job_description'),
                    'post_link': job.get('post_link'),
                    'keywords': job.get('keywords'),
                    'match_score': scores['overall'],
                    'skill_score': scores['skill_score'],
                    'exp_score': scores['exp_score'],
                    'title_score': scores['title_score']
                })

        if len(results) == 0:
            print(f"\n No jobs found above {min_score:.0%} threshold")
            print("💡 Try lowering min_score to 0.1 or check if your resume has skills")
            return pd.DataFrame()
        
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('match_score', ascending=False)
        top_results = results_df.head(top_n)
        
        print(f"\n Found {len(results_df)} jobs above {min_score:.0%} threshold")
        print(f" Returning top {len(top_results)} matches")
        
        return top_results


# ==================================================
# TEST FUNCTION
# ==================================================
# def test_matcher():
#     """Test the matcher with your resume"""
    
#     import sys
#     import os
#     sys.path.append('..')
    
#     print("="*60)
#     print("JOB MATCHER TEST")
#     print("="*60)
    
#     # Load and analyze resume
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     pdf_path = os.path.join(BASE_DIR, '..', 'data', 'Saro_Elza_Mathew_Resume.pdf')
    
#     with open(pdf_path, 'rb') as f:
#         resume_text = extract_text_from_pdf(f)
    
#     print(f"\n📄 Extracted resume: {len(resume_text)} chars")
    
#     resume_data = analyze_resume(resume_text)
#     if resume_data is None:
#         print("❌ Resume analysis failed — cannot continue job matching.")
#         return
    
#     print(f"\n✅ Resume analyzed:")
#     print(f"   - Skills: {resume_data.get('skills', [])[:5]}")
#     print(f"   - Experience: {resume_data.get('experience_years')} years")
#     print(f"   - Level: {resume_data.get('career_level')}")
    
#     # Initialize matcher
#     csv_path = os.path.join(BASE_DIR, '..', 'data', 'tech_jobs_data.csv')
#     matcher = JobMatcher(csv_path)
    
#     # Find matches
#     matches = matcher.finding_matching_jobs(resume_data, top_n=10, min_score=0.25)
    
#     if len(matches) == 0:
#         print("\n⚠️  No matches found. Try lowering min_score.")
#         return
    
#     # Display results
#     print("\n" + "="*60)
#     print("TOP 10 MATCHING JOBS")
#     print("="*60)
    
#     for i, (idx, job) in enumerate(matches.iterrows(), 1):
#         print(f"\n{i}. {job['title']}")
#         print(f"   🏢 Company: {job['company']}")
#         print(f"   📍 Location: {job['location']}")
#         print(f"   📊 Level: {job['experience_level']}")
#         print(f"   🎯 Match: {job['match_score']*100:.1f}%")
#         print(f"      └─ Skills: {job['skill_score']*100:.0f}% | Experience: {job['exp_score']*100:.0f}% | Title: {job['title_score']*100:.0f}%")
        
#         # Show description preview
#         desc = str(job['description'])[:200].replace('\n', ' ')
#         print(f"   📝 {desc}...")
        
#         # Show link if available
#         if pd.notna(job.get('post_link')):
#             print(f"   🔗 {job['post_link']}")

# if __name__ == "__main__":
#     test_matcher()