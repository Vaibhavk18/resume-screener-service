# 🚀 Resume Screener API

An intelligent **FastAPI-based backend** that automates resume screening by parsing uploaded resumes (PDF/DOCX/TXT), extracting structured data (name, email, skills, experience), and scoring candidates against job descriptions.  
Built with **PostgreSQL**, **AWS S3**, **RDS**, and **ECS Fargate** for scalable cloud deployment.

---

## 🧩 Tech Stack

- **Backend:** FastAPI (Python 3.11)  
- **Database:** PostgreSQL (AWS RDS)  
- **Storage:** AWS S3 (for resume uploads)  
- **Containerization:** Docker + Docker Compose  
- **Cloud Deployment:** AWS ECS (Fargate) + ECR  
- **NLP Processing:** spaCy + SentenceTransformers (BERT)  
- **Authentication:** JWT (JSON Web Tokens)  

---

## ⚙️ Features

✅ Upload resumes (PDF, DOCX, TXT)  
✅ Extract candidate name, email, skills, and total experience  
✅ Skill matching and resume scoring via BERT embeddings  
✅ Store resume metadata + S3 URLs in PostgreSQL (RDS)  
✅ JWT-secured endpoints for HR users  
✅ Fully containerized and deployed on AWS ECS  
✅ Automatic resume text extraction using `pdfplumber` and `docx2txt`

#### 2. Configure AWS Services
- **RDS** → PostgreSQL instance for persistent data  
- **S3** → Bucket for storing uploaded resumes  
- **ECS (Fargate)** → Container orchestration  
- **IAM Roles** → Grant ECS access to RDS + S3  

#### 3. Environment Variables (ECS Task Definition)
```env
DATABASE_URL=postgresql+psycopg://user:password@your-rds-endpoint:5432/postgres
S3_BUCKET=resume-screener-bucket
AWS_REGION=eu-north-1
AWS_ACCESS_KEY_ID=<your_aws_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret>
```
## 🧠 NLP Pipeline

1. **Text Extraction:** `pdfplumber` or `docx2txt`
2. **Field Extraction:** Regex + spaCy NER
3. **Skill Detection:** Keyword matching with an extended tech vocabulary
4. **Semantic Scoring:** SentenceTransformer model (`all-MiniLM-L6-v2`)
5. **Resume Ranking:** Cosine similarity → 0–100 scoring

## 📄 License
MIT License © 2025 Vaibhav Vishal