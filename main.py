from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from pathlib import Path

app = FastAPI(title="Ascol Hub AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = json.loads((Path(__file__).parent / "knowledge.json").read_text(encoding="utf-8"))


class Ask(BaseModel):
    question: str
    section: str | None = None


def score(text: str, query: str) -> int:
    words = [w for w in query.lower().split() if len(w) > 2]
    hay = text.lower()
    return sum(1 for w in words if w in hay)


@app.get("/health")
def health():
    return {"ok": True, "service": "ascol-hub-ai"}


@app.post("/ask")
def ask(body: Ask):
    q = body.question.strip()
    best = None
    best_s = 0
    sources = "Python knowledge base"
    place = None
    for item in DATA:
        s = score(item["text"], q)
        if s > best_s:
            best_s = s
            best = item
            place = item.get("mapPlaceId")
    if not best or best_s == 0:
        return {
            "answer": "I only answer from ASCOL-approved hub data. Ask about exam forms, library, CSIT, labs, or internals.",
            "sources": [sources],
        }
    return {"answer": best["answer"], "sources": [sources, best.get("source", "hub")], "mapPlaceId": place}
