# Example 1: Short text (no truncation needed)
text1 = "Hello World"
result1 = text1[:4000]
print(f"Original: {len(text1)} chars")
print(f"After: {len(result1)} chars")
print(f"Text: {result1}")

# Example 2: Long text (truncation happens)
text2 = "A" * 10000  # 10,000 'A' characters
result2 = text2[:4000]
print(f"\nOriginal: {len(text2)} chars")
print(f"After: {len(result2)} chars")

# Example 3: Your actual resume
from utils.pdf_handler import extract_text_from_pdf

with open(r"data\Saro_Elza_Mathew_Resume.pdf", 'rb') as f:
    resume_text = extract_text_from_pdf(f)
    
print(f"\nYour resume: {len(resume_text)} chars")

truncated = resume_text[:4000]
print(f"After truncation: {len(truncated)} chars")
print(f"\nFirst 200 chars:\n{truncated[:200]}")
print(f"\nLast 200 chars:\n{truncated[-200:]}")