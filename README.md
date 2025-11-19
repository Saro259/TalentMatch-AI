# 🧠 AI-Job-Matcher

## 📌 Overview

This project, AI-Job-Matcher, is designed to help users find the best job matches based on their resume. It leverages AI to analyze resume content and compare it with job postings to identify relevant opportunities.

## ⭐ Key Features & Benefits

*   **Resume Analysis:** Extracts key skills, experience, and qualifications from uploaded resumes.
*   **Job Matching:** Compares resume data with job descriptions to calculate a relevance score.
*   **Streamlit Interface:** Provides an intuitive web interface for easy resume upload and job matching.
*   **AI Powered:** Uses Groq's API for advanced analysis and matching capabilities.

## 🧩 Prerequisites & Dependencies

Before running this project, ensure you have the following installed:

*   **Python:** (version 3.7 or higher recommended)
*   **pip:** Python package installer.

The project also depends on the following Python libraries:

*   streamlit
*   pypdf
*   python-dotenv
*   groq
*   plotly
*   pandas

These dependencies are listed in the `requirements.txt` file.

## 🔧 Installation & Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Saro259/AI-Job-Matcher.git
    cd AI-Job-Matcher
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**

    *   Create a `.env` file in the project root directory.
    *   Add your Groq API key to the `.env` file:

        ```
        GROQ_API_KEY=YOUR_GROQ_API_KEY
        ```

        Replace `YOUR_GROQ_API_KEY` with your actual Groq API key. You can obtain an API key from the Groq website.

## 🚀 Usage Examples & API Documentation

1.  **Run the Streamlit Application:**

    ```bash
    streamlit run app.py
    ```

    This will start the Streamlit application, and you can access it in your web browser at the address displayed in the console (usually `http://localhost:8501`).

2.  **Using the Application:**

    *   Upload your resume in PDF format using the file uploader.
    *   The application will process your resume and display potential job matches.

## ⚙️ Configuration Options

*   **Groq API Key:** The Groq API key is configured via the `.env` file. Ensure this key is correctly set up for the AI analysis to function properly.
*   **Jobs CSV Path:** The `JobMatcher` class (in `utils/jobs_matcher.py`) uses a CSV file containing job posting data. The path to this CSV file is specified during the initialization of the `JobMatcher` object. Ensure the path is correct. The application expects the CSV file to be named as 'filtered_jobs.csv' and residing in the same directory as `jobs_matcher.py`.

## 📁 Project Structure

├── .gitignore

├── app.py # Main Streamlit application file

├── requirements.txt # List of Python dependencies

└── utils/ # Utility modules

├── init.py

├── groq_analyzer.py # Module for analyzing resumes using Groq API

├── jobs_matcher.py # Module for matching resumes with job postings

└── pdf_handler.py # Module for extracting text from PDF files


### 📄 Important Files

*   **`app.py`**:  The main script that launches the Streamlit application. It handles the user interface, file uploads, and calls the necessary functions for resume analysis and job matching.
*   **`requirements.txt`**: Lists all the Python packages required to run the application. Use `pip install -r requirements.txt` to install them.
*   **`utils/groq_analyzer.py`**: Contains functions to analyze resumes using the Groq API. It extracts relevant information for job matching.
*   **`utils/jobs_matcher.py`**: Contains the `JobMatcher` class, which is responsible for matching resume data with job postings and calculating relevance scores.
*   **`utils/pdf_handler.py`**: Contains functions to extract text from uploaded PDF files.

## 🤝 Contributing Guidelines

Contributions are welcome! To contribute to this project:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive messages.
4.  Push your changes to your forked repository.
5.  Submit a pull request to the main repository.

Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## 📜 License Information

This project is licensed under the MIT License.

## 🙏 Acknowledgments

*   Streamlit for providing a simple and efficient way to create web applications.
*   Groq for their AI API.
*   pypdf for PDF handling capabilities.
