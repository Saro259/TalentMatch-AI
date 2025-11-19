import streamlit as st
import os
import pandas as pd
from utils.jobs_matcher import JobMatcher
from utils.pdf_handler import extract_text_from_pdf
from utils.groq_analyzer import analyze_resume

# ---- Basic Streamlit Page Setup ----
st.set_page_config(page_title="AI Job Matcher", page_icon="🎯", layout="centered")

st.title("🎯 AI Job Matcher")
st.caption("Upload your resume and let AI find the best job matches for you.")

# ---- Upload Resume ----
uploaded_file = st.file_uploader("📄 Upload your Resume (PDF only)", type=["pdf"])

# ---- User Options ----
num_results = st.slider("Number of job results to display", 5, 30, 10)
# min_score = st.slider("Minimum match score (%)", 10, 80, 30) / 100

# ---- Handle Uploaded Resume ----
if uploaded_file is not None:
    if st.button("🔍 Analyze Resume & Find Jobs"):
        try:
            with st.spinner("🤖 Reading your resume and searching jobs..."):
                # Step 1: Extract resume text
                resume_text = extract_text_from_pdf(uploaded_file)

                # Step 2: Analyze resume (Groq Analyzer)
                resume_data = analyze_resume(resume_text)
                if resume_data is None:
                    st.error("❌ Resume analysis failed. Please try again.")
                    st.stop()

                # Step 3: Initialize JobMatcher
                csv_path = os.path.join("data", "tech_jobs_data.csv")
                matcher = JobMatcher(csv_path)

                # Step 4: Find matches
                matches = matcher.finding_matching_jobs(
                    resume_data,
                    top_n=num_results,
                    min_score=min_score
                )

            # ---- Display Results ----
            if len(matches) > 0:
                st.success(f"✅ Found {len(matches)} matching jobs!")
                st.subheader("💼 Top Matching Jobs")

                for i, (_, job) in enumerate(matches.iterrows(), 1):
                    st.markdown(f"**{i}. {job['title']}**  —  {job['company']}")
                    st.caption(f"📍 {job['location']} | 📊 Level: {job['experience_level']} | 🎯 Match: {job['match_score']*100:.0f}%")

                    if pd.notna(job.get('post_link')):
                        st.link_button("🔗 Apply Now", job['post_link'])

                    # Optional description preview
                    desc = str(job['description'])[:300].replace('\n', ' ')
                    st.write(f"📝 {desc}...")
                    st.divider()

                # ---- Export Option ----
                csv_data = matches.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_data,
                    file_name="job_matches.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            else:
                st.warning("No job matches found. Try lowering the minimum match score.")

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")

else:
    st.info("👈 Upload your resume (PDF) to start job matching.")
