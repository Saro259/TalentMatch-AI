import os
import json
# import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

def analyze_resume(resume_text: str) -> dict:
    """
    Analyze resume and extract information for job matching.
    
    Returns:
        dict: Job-matching relevant data or None if extraction fails
    """
    
    # ============================================
    # STEP 1: Truncate Input
    # ============================================
    print(f"Original resume: {len(resume_text)} chars")
    max_char = 4000
    
    if len(resume_text) <= max_char:
        prepared_text = resume_text
    else:
        truncated = resume_text[:max_char]
        last_spaced_index = truncated.rfind(' ')
        if last_spaced_index > 0:
            prepared_text = truncated[:last_spaced_index]
        else:
            prepared_text = truncated
        print(f"Truncated from {len(resume_text)} to {len(prepared_text)} chars")
    
    resume_text = prepared_text
    print(f"After truncation: {len(resume_text)} chars")

    # ============================================
    # STEP 2: Build Prompt
    # ============================================
    system_message = """You are an expert resume parser specializing in extracting job-matching information.
Your task is to analyze resumes and extract data useful for matching candidates with job opportunities.
Always return valid JSON only, with no extra text."""

    user_prompt = f"""Analyze this resume and extract information relevant for job matching.

RESUME TEXT:
{resume_text}

Return ONLY a valid JSON object (no markdown, no code blocks) with these exact fields:
{{
    "skills": ["skill1", "skill2"],
    "experience_years": 2.5,
    "past_roles": ["role1", "role2"],
    "current_role": "most recent title",
    "domain": "industry sector",
    "projects": ["project1", "project2"],
    "education_level": "highest degree",
    "technologies": ["tech1", "tech2"],
    "career_level": "Entry/Mid/Senior/Lead",
    "work_preferences": "Remote/Hybrid/Onsite/Flexible",
    "key_achievements": ["achievement1"],
    "desired_roles": ["role1", "role2"]
}}

EXTRACTION INSTRUCTIONS:
1. skills: Extract ALL technical and soft skills (minimum 5)
2. experience_years: Calculate total years as DECIMAL (e.g., 2.5, 3.7)
3. past_roles: List 3-5 previous job titles
4. current_role: Most recent position
5. domain: Industry (FinTech, EdTech, SaaS, etc.)
6. projects: 3-5 key projects with achievements
7. education_level: Highest degree and field
8. technologies: Specific tools/languages (minimum 5)
9. career_level: Entry/Mid/Senior/Lead based on experience
10. work_preferences: Remote/Hybrid/Onsite/Flexible
11. key_achievements: Quantifiable results
12. desired_roles: Infer 2-3 next career steps

DEFAULTS for missing data:
- Lists: []
- Numbers: 0
- Strings: "Not specified"

Return ONLY the JSON object. Start with {{ and end with }}.
"""

    # ============================================
    # STEP 3: Call Gemini API
    # ============================================
    # try:
    #     print("\n🤖 Analyzing with Gemini AI...")
        
    #     # Combine prompts (Gemini doesn't have separate system role)
    #     full_prompt = system_message + "\n\n" + user_prompt
        
    #     # Initialize model
    #     model = genai.GenerativeModel('gemini-2.5-flash')
        
    #     # Generate response
    #     response = model.generate_content(
    #         full_prompt,  # ← Pass string directly
    #         generation_config={
    #             "temperature": 0.3,
    #             "max_output_tokens": 1500,
    #         }
    #     )
        
    #     content = response.text
    #     print(f"Received response ({len(content)} chars)")
        
    # except Exception as e:
    #     print(f"API Error: {e}")
    #     return None
    
    try:
        print("\n🤖 Analyzing with Llama AI...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        content = response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return None

    # ============================================
    # STEP 4: Clean Response
    # ============================================
    if '```json' in content:
        content = content.split('```json')[1].split('```')[0]
    elif '```' in content:
        content = content.split('```')[1].split('```')[0]
    
    content = content.strip()
    
    # ============================================
    # STEP 5: Parse JSON
    # ============================================
    try:
        result = json.loads(content)
        print("JSON parsed successfully!")
        
    except json.JSONDecodeError as e:
        print(f"JSON Error: {str(e)}")
        print(f"Response was: {content[:300]}...")
        return None  # ← Fixed: return None
    
    # ============================================
    # STEP 6: Validate and Fix Data
    # ============================================
    
    # Ensure experience_years is float
    if 'experience_years' in result:
        result['experience_years'] = float(result['experience_years'])
    
    # Fallback if AI returned 0 but resume has work history
    if result.get('experience_years', 0) == 0:
        num_roles = len(result.get('past_roles', []))
        if num_roles > 0:
            estimated_years = round(num_roles * 1.5, 1)
            result['experience_years'] = estimated_years
            print(f"AI returned 0 years but found {num_roles} roles")
            print(f"   → Estimated {estimated_years} years")
    
    print(f"Experience: {result.get('experience_years', 0)} years")
    
    # ============================================
    # STEP 7: Validate Required Fields
    # ============================================
    required_fields = [
        'skills', 'experience_years', 'past_roles', 'current_role',
        'domain', 'projects', 'education_level', 'technologies',
        'career_level', 'work_preferences', 'key_achievements', 'desired_roles'
    ]
    
    for field in required_fields:
        if field not in result:
            print(f"Warning: Missing field '{field}'")
            
            # Add default based on type
            if field in ['skills', 'past_roles', 'projects', 'technologies', 
                        'key_achievements', 'desired_roles']:
                result[field] = []
            elif field == 'experience_years':
                result[field] = 0.0
            else:
                result[field] = "Not specified"
    
    return result