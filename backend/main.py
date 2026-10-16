"""Small local demo API for Sapna Saathi. All opportunities and rules are illustrative."""
from __future__ import annotations

import json
import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import ai_service

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("SAPNA_SAATHI_DB", str(BASE_DIR / "sapna_saathi.db")))
DOCUMENT_IDS = {"aadhaar", "marksheet", "income", "bank", "photo", "caste"}
STUDENT_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,80}$")

OPPORTUNITIES = [
    {"id": "post", "title": "Post-Matric Scholarship (mock)", "org": "Illustrative provider - not verified", "tag": "POST-MATRIC - MOCK", "amount": "Example: Rs 12,000", "period": "per year - mock", "desc": "Mock example of support for students continuing education after Class 10.", "criteria": "Demo rule: Class 11 or above - income limit shown for illustration only", "is_mock": True},
    {"id": "rural", "title": "Rural Talent Scholarship (mock)", "org": "Illustrative provider - not verified", "tag": "RURAL TALENT - MOCK", "amount": "Example: Rs 25,000", "period": "one-time - mock", "desc": "Mock example of support for talented students from rural communities.", "criteria": "Demo rule: rural resident - marks threshold shown for illustration only", "is_mock": True},
    {"id": "kanya", "title": "Kanya Shiksha Protsahan (mock)", "org": "Illustrative provider - not verified", "tag": "GIRLS EDUCATION - MOCK", "amount": "Example: Rs 15,000", "period": "per year - mock", "desc": "Mock example encouraging girls to continue into higher education.", "criteria": "Demo rule: female student - enrollment rule shown for illustration only", "is_mock": True},
]

class Profile(BaseModel):
    class Config:
        extra = "forbid"
    name: str = Field(default="", max_length=120)
    age: str = Field(default="", max_length=3)
    state: str = Field(default="Madhya Pradesh", max_length=80)
    district: str = Field(default="", max_length=100)
    category: str = Field(default="General", max_length=50)
    gender: str = Field(default="Female", max_length=40)
    classLevel: str = Field(default="12th pass", max_length=80)
    course: str = Field(default="BA / BSc", max_length=100)
    marks: str = Field(default="", max_length=6)
    income: str = Field(default="", max_length=12)
    rural: bool = True

    @validator("age")
    def validate_age(cls, value: str) -> str:
        cls._validate_number(value, "age", 120)
        if value and float(value) < 10:
            raise ValueError("age must be at least 10")
        return value

    @validator("marks")
    def validate_marks(cls, value: str) -> str:
        cls._validate_number(value, "marks", 100)
        return value

    @validator("income")
    def validate_income(cls, value: str) -> str:
        cls._validate_number(value, "income", 1_000_000_000)
        return value

    @staticmethod
    def _validate_number(value: str, field: str, maximum: float) -> None:
        if value:
            try:
                parsed = float(value)
            except ValueError as exc:
                raise ValueError(f"{field} must be numeric") from exc
            if parsed < 0 or parsed > maximum:
                raise ValueError(f"{field} must be between 0 and {maximum:g}")

class EligibilityRequest(BaseModel):
    class Config:
        extra = "forbid"
    profile: Profile
    opportunity_ids: list[str] | None = Field(default=None, max_length=20)

class DocumentProgress(BaseModel):
    class Config:
        extra = "forbid"
    checked: list[str] = Field(default_factory=list)

    @validator("checked")
    def validate_document_ids(cls, value: list[str]) -> list[str]:
        if len(value) > len(DOCUMENT_IDS):
            raise ValueError("checked may contain at most six document ids")
        if any(item not in DOCUMENT_IDS for item in value):
            raise ValueError("checked contains an unknown document id")
        return value

class AssistantContext(BaseModel):
    class Config:
        extra = "forbid"
    class_level: str = Field(default="", max_length=80)
    course: str = Field(default="", max_length=100)
    rural: bool | None = None
    completed_documents: list[str] = Field(default_factory=list)

    @validator("completed_documents")
    def validate_completed_documents(cls, value: list[str]) -> list[str]:
        if len(value) > len(DOCUMENT_IDS) or any(item not in DOCUMENT_IDS for item in value):
            raise ValueError("completed_documents contains invalid document ids")
        return value

class ChatMessage(BaseModel):
    class Config:
        extra = "forbid"
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)

class ChatRequest(BaseModel):
    class Config:
        extra = "forbid"
    question: str = Field(min_length=1, max_length=1500)
    context: AssistantContext = Field(default_factory=AssistantContext)
    history: list[ChatMessage] = Field(default_factory=list)

    @validator("question")
    def validate_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must not be blank")
        return value

    @validator("history")
    def validate_history(cls, value: list[ChatMessage]) -> list[ChatMessage]:
        if len(value) > 8:
            raise ValueError("history may contain at most eight messages")
        return value

class GuidanceRequest(BaseModel):
    class Config:
        extra = "forbid"
    document_id: str
    context: AssistantContext = Field(default_factory=AssistantContext)

    @validator("document_id")
    def validate_document_id(cls, value: str) -> str:
        if value not in ai_service.DOCUMENT_GUIDANCE:
            raise ValueError("unknown document id")
        return value

@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()

def initialize_db() -> None:
    with connection() as db:
        db.execute("CREATE TABLE IF NOT EXISTS profiles (student_id TEXT PRIMARY KEY, profile_json TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        db.execute("CREATE TABLE IF NOT EXISTS documents (student_id TEXT PRIMARY KEY, checked_json TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")

initialize_db()
app = FastAPI(title="Sapna Saathi Demo API", version="1.0.0", description="Local demo only. Scholarship data and eligibility rules are illustrative, not official.")
CORS_ORIGINS = [origin.strip().rstrip("/") for origin in os.getenv("SAPNA_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["GET", "POST", "PUT", "OPTIONS"], allow_headers=["*"])

@app.on_event("startup")
async def log_ai_provider_configuration() -> None:
    ai_service.log_provider_key_status("API startup")

def validate_student_id(student_id: str) -> None:
    if not STUDENT_ID_RE.fullmatch(student_id):
        raise HTTPException(status_code=400, detail="student_id must contain 1-80 letters, numbers, underscores, or hyphens")

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Sapna Saathi demo API", "data": "mock"}

@app.get("/api/opportunities")
def opportunities() -> list[dict[str, object]]:
    return OPPORTUNITIES

def evaluate(profile: Profile, opportunity_id: str) -> tuple[bool, str]:
    study = f"{profile.classLevel} {profile.course}".lower()
    if opportunity_id == "post":
        ok = any(term in study for term in ("11th", "12th", "college", "graduat", "diploma", "iti")) and (not profile.income or float(profile.income) <= 250000)
        return ok, "Matches the demo study and income rules." if ok else "Does not match the demo study or income rules."
    if opportunity_id == "rural":
        ok = profile.rural and (not profile.marks or float(profile.marks) >= 60)
        return ok, "Matches the demo rural residence and marks rules." if ok else "Does not match the demo rural residence or marks rules."
    if opportunity_id == "kanya":
        ok = profile.gender == "Female" and any(term in study for term in ("college", "graduat", "diploma", "iti", "ba", "bsc"))
        return ok, "Matches the demo gender and enrollment rules." if ok else "Does not match the demo gender or enrollment rules."
    raise HTTPException(status_code=400, detail=f"Unknown opportunity id: {opportunity_id}")

@app.post("/api/eligibility/check")
def check_eligibility(request: EligibilityRequest) -> list[dict[str, object]]:
    ids = request.opportunity_ids or [str(item["id"]) for item in OPPORTUNITIES]
    if len(ids) != len(set(ids)):
        raise HTTPException(status_code=400, detail="opportunity_ids must not contain duplicates")
    return [{"opportunity_id": item_id, "eligible": evaluate(request.profile, item_id)[0], "reason": evaluate(request.profile, item_id)[1], "is_mock": True} for item_id in ids]

@app.post("/api/assistant/chat")
async def assistant_chat(request: ChatRequest) -> dict[str, str]:
    context = request.context.dict()
    history = [message.dict() for message in request.history]
    return await ai_service.chat(request.question, history, context)

@app.post("/api/assistant/guidance")
async def assistant_guidance(request: GuidanceRequest) -> dict[str, str]:
    return await ai_service.guidance(request.document_id, request.context.dict())

@app.get("/api/profile/{student_id}")
def get_profile(student_id: str) -> dict[str, object]:
    validate_student_id(student_id)
    with connection() as db:
        row = db.execute("SELECT profile_json FROM profiles WHERE student_id = ?", (student_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"student_id": student_id, "profile": json.loads(row["profile_json"])}

@app.put("/api/profile/{student_id}")
def put_profile(student_id: str, profile: Profile) -> dict[str, object]:
    validate_student_id(student_id)
    payload = profile.dict()
    with connection() as db:
        db.execute("INSERT INTO profiles(student_id, profile_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(student_id) DO UPDATE SET profile_json=excluded.profile_json, updated_at=CURRENT_TIMESTAMP", (student_id, json.dumps(payload)))
    return {"student_id": student_id, "profile": payload, "saved": True}

@app.get("/api/documents/{student_id}")
def get_documents(student_id: str) -> dict[str, object]:
    validate_student_id(student_id)
    with connection() as db:
        row = db.execute("SELECT checked_json FROM documents WHERE student_id = ?", (student_id,)).fetchone()
    return {"student_id": student_id, "checked": json.loads(row["checked_json"]) if row else []}

@app.put("/api/documents/{student_id}")
def put_documents(student_id: str, progress: DocumentProgress) -> dict[str, object]:
    validate_student_id(student_id)
    checked = sorted(set(progress.checked))
    with connection() as db:
        db.execute("INSERT INTO documents(student_id, checked_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(student_id) DO UPDATE SET checked_json=excluded.checked_json, updated_at=CURRENT_TIMESTAMP", (student_id, json.dumps(checked)))
    return {"student_id": student_id, "checked": checked, "saved": True}
