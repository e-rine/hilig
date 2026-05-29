# FILENAME: app.py
# Run: python -m uvicorn app:app --reload  (from backend/ folder)

import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from core.spell_checker import SpellChecker

# ── Globals ────────────────────────────────────────────────────────────────── #

checker = SpellChecker()
WORDLIST_PATH = os.path.join(os.path.dirname(__file__), "data", "hiligaynon_wordlist.txt")

# ── Lifespan (runs once on startup) ───────────────────────────────────────── #

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading Hiligaynon wordlist into BK-Tree...")
    if os.path.exists(WORDLIST_PATH):
        with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        checker.load_wordlist(words)
        print(f"  OK: {checker.wordlist_size} words loaded.")
    else:
        print(f"  WARNING: wordlist not found at {WORDLIST_PATH}")
    yield

# ── App (must be created BEFORE any @app decorators) ──────────────────────── #

app = FastAPI(title="Hiligaynon Spell Checker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────────────────── #

@app.get("/api/check")
def check_spelling(word: str = Query(..., description="Word to spell-check")):
    if not word or not word.strip():
        raise HTTPException(status_code=400, detail="word must not be empty")
    return {
        "word": word,
        "correct": checker.is_correct(word),
        "suggestions": checker.check(word),
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "words_loaded": checker.wordlist_size}

# ── Serve frontend (mount LAST so /api routes aren't shadowed) ─────────────── #

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")