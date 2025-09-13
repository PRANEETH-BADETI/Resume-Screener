# 📄 AI-Powered Resume Screener  

An **AI-powered resume screening tool** built using **Streamlit** to help recruiters and hiring managers efficiently rank candidates by comparing resumes against a job description. It leverages **NLP techniques** and **Google Gemini-1.5-Flash API** to provide a **relevance score** and a **concise recruiter-friendly summary** for each candidate.  

---

## 🚀 Features  

- 🎨 **Intuitive UI** – Simple and clean interface built with **Streamlit**.  
- 📂 **Multi-format Document Parsing** – Supports **PDF, DOCX, and TXT** resumes and job descriptions.  
- 🔍 **Semantic Search** – Uses **Sentence-Transformers** to calculate semantic relevance between resumes and job descriptions.  
- 🤖 **AI-Powered Analysis** – Integrates **Google Gemini-1.5-Flash** to generate summaries highlighting **key strengths and gaps**.  
- 📊 **Historical Data Storage** – Stores all screening sessions in **PostgreSQL** for easy revisit and analysis.  
- ⚡ **Scalable Backend** – Built on **PostgreSQL** for reliable, persistent storage.  

---

## 🛠️ Tech Stack  

- **Framework:** [Streamlit](https://streamlit.io/)  
- **NLP:** spaCy, Sentence-Transformers, NLTK  
- **AI:** Google Gemini-1.5-Flash API  
- **Database:** PostgreSQL  
- **Python Libraries:** psycopg2, PyPDF2, python-docx, python-dotenv, firebase-admin  

---

## ⚙️ Setup and Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-username/Resume-Screener.git
cd Resume-Screener
```

### 2️⃣ Install Dependencies  
```bash
pip install -r requirements.txt
```

### 3️⃣ Set up the Database  
- Ensure PostgreSQL is running locally or hosted.  
- Create a `.env` file in your project directory with database credentials:  

```ini
DB_NAME="your_db_name"
DB_USER="your_username"
DB_PASSWORD="your_password"
DB_HOST="localhost"
DB_PORT="5432"
```

- Run the database setup script:  
```bash
python database_setup.py
```

### 4️⃣ Configure Gemini API Key  
- Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/).  
- Add it to `.streamlit/secrets.toml`:  

```toml
[api]
GEMINI_API_KEY = "your_gemini_api_key"
```

### 5️⃣ Download spaCy Model  
```bash
python -m spacy download en_core_web_sm
```

---

## ▶️ Running the Application  

```bash
streamlit run app.py
```

👉 This will open the app in your default browser.  

---

## 📸 Demo (Optional)  
_Add screenshots or GIFs of your app here._  

---

## 📂 Project Structure  

```
Resume-Screener/
│── app.py                # Main Streamlit app
│── db/                 
    └── database_setup.py # Script to initialize PostgreSQL tables
    └── db_manager.py      
│── requirements.txt      # Dependencies
│── .env                  # Environment variables (DB credentials)
│── .streamlit/
│   └── secrets.toml      # API key storage
│── utils/                # Helper scripts (parsing, scoring, etc.)
    └── data_parser.py
    └── nlp_processor.py 
```

---

## 🔮 Future Improvements  

- ✅ Add **support for more document formats** (LinkedIn exports).  
- ✅ Implement **real-time feedback loop** to fine-tune AI summaries.  
- ✅ Build **role-based authentication** for recruiters & hiring managers.  
- ✅ Deploy on **AWS / GCP / Heroku** for production use.  

---
