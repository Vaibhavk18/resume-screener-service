import re
from typing import Dict, List, Optional

try:  # make spaCy optional for environments without wheels
    import spacy as _spacy  # type: ignore
except Exception:
    _spacy = None  # type: ignore


def _get_nlp_model():
    if _spacy is None:
        return None
    try:
        return _spacy.load("en_core_web_sm")
    except Exception:
        try:
            return _spacy.blank("en")
        except Exception:
            return None


NLP = _get_nlp_model()

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

DEFAULT_SKILLS = {
     # Programming Languages
    "python", "java", "javascript", "typescript", "c", "c++", "go", "rust", "r",
    
    # Frameworks & Libraries
    "fastapi", "flask", "django", "react", "nextjs", "vue", "angular", 
    "nodejs", "express", "spring", "dotnet", "pandas", "numpy", 
    "matplotlib", "tensorflow", "pytorch", "scikit-learn", "transformers", 
    "beautifulsoup", "opencv", "streamlit",
    
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "jenkins",
    "git", "github", "gitlab", "ci/cd", "linux", "bash", "nginx", "heroku",
    
    # Data Engineering
    "sql", "mysql", "postgresql", "mongodb", "redis", "snowflake", 
    "bigquery", "hive", "spark", "hadoop", "airflow", "kafka",
    
    # Tools & Analytics
    "excel", "power bi", "tableau", "looker", "jira", "confluence", 
    "notion", "vs code", "pycharm", "intellij","postman","prometheus","grafana","figma",
    
    # ML/NLP Topics
    "machine learning", "deep learning", "data science", "nlp", 
    "computer vision", "llm", "data analysis", "predictive modeling",
    
    # Soft/Business Skills
    "leadership", "communication", "teamwork", "problem solving", 
    "project management", "agile", "scrum","product management","ux/ui design","sdlc",

}


def extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_name(text: str) -> Optional[str]:
    # Use NER PERSON entity if spaCy model is available, else heuristic from first lines
    if NLP is not None:
        doc = NLP(text)
        for ent in getattr(doc, "ents", []):
            if getattr(ent, "label_", "") == "PERSON" and 2 <= len(ent.text.split()) <= 4:
                return ent.text
    first_lines = [l.strip() for l in text.splitlines()[:5] if l.strip()]
    if first_lines:
        candidate = first_lines[0]
        if 2 <= len(candidate.split()) <= 4 and not EMAIL_REGEX.search(candidate):
            return candidate
    return None


def extract_skills(text: str, vocabulary: Optional[List[str]] = None) -> List[str]:
    vocab = set((vocabulary or []) + list(DEFAULT_SKILLS))
    text_lower = text.lower()
    found = []
    for skill in sorted(vocab):
        tokens = skill.split()
        pattern = r"\b" + r"\s+".join([re.escape(t) for t in tokens]) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found), key=lambda s: s.lower())


def extract_experience_years(text: str) -> Optional[int]:
    # Simple heuristic: capture patterns like 'X years' up to 40
    matches = re.findall(r"(\d{1,2})\s+years", text.lower())
    candidates = [int(m) for m in matches if 0 < int(m) <= 40]
    return max(candidates) if candidates else None


def extract_fields(text: str) -> Dict[str, Optional[str]]:
    name = extract_name(text)
    email = extract_email(text)
    skills = extract_skills(text)
    experience = extract_experience_years(text)
    return {
        "candidate_name": name,
        "candidate_email": email,
        "skills": ", ".join(skills) if skills else None,
        "total_experience_years": experience,
    } 