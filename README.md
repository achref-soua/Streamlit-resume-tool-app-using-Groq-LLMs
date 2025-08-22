# Resume Tool App

A modular, secure, and user-friendly Streamlit application for building, adapting, and enhancing resumes using Groq LLM.

## Features

- **User Authentication**: Sign up, log in, and log out securely. Passwords are hashed and stored in a private database.
- **Resume Builder**: Create, edit, duplicate, delete, and visualize multiple resumes. Add sections like summary, experience, education, projects, skills, certificates, publications, and contact info. Dynamic forms allow adding/removing entries for each section.
- **Resume Adaptation**: Select a resume and adapt it to a job description using Groq LLM. Results are editable and can be saved as a new resume or overwrite the original.
- **Resume Enhancement**: Select a resume and enhance it using Groq LLM. Receive constructive feedback and save the improved version.
- **Security**: Credentials and database files are excluded from version control. All sensitive data is stored locally and securely.
- **Modern UI**: Clean sidebar navigation and intuitive forms for a smooth user experience.

## Folder Structure

```
resume-tool-app/
├── app.py                # Main Streamlit entry point
├── auth.py               # Authentication logic
├── resume_builder.py     # Resume builder UI and logic
├── resume_storage.py     # Resume CRUD and database
├── resume_adapter.py     # Resume adaptation via Groq API
├── resume_enhancer.py    # Resume enhancement via Groq API
├── utils.py              # Helper functions
├── db/                   # SQLite database files (ignored by git)
├── .env                  # API keys (ignored by git)
├── .gitignore            # Ignore sensitive files
└── README.md             # Project documentation
```

## Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install streamlit bcrypt langchain_groq python-dotenv
   ```
3. **Add your Groq API key** to a `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## Usage

- Use the sidebar to navigate between authentication, resume builder, adaptation, and enhancement features.
- All resumes and user data are stored locally in the `db/` folder.
- API keys and database files are excluded from git for security.

## Security Notes
- Passwords are hashed using bcrypt.
- All sensitive files are ignored by git via `.gitignore`.
- API keys are loaded from `.env` and never exposed in code or version control.

## License

MIT

## Author

Achref Soua
