# FILENAME: app.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# placeholder palang ni guys
# spell_checker na di siya dapat
def check(word: str) -> list:
    return [word, "placeholder1", "placeholder2"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs on startup before server accepts requests
    print("Loading Hiligaynon Wordlist into BK-Tree...")
    yield

app = FastAPI(lifespan=lifespan)

# CORS configuration permits local frontend file to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/check")
def check_spelling(word: str = Query(..., description="The word to look up")):
    # endpoint that accpets a word and returns suggestions
    suggestions = check(word)
    return {
        "word": word,
        "suggestions": suggestions
    }

# serve frontend statically
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")