from fastapi import FastAPI
import os
import aiosqlite
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
  await init_db()
  yield

app = FastAPI(lifespan=lifespan)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "notes.db")

async def init_db():
  os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
  async with aiosqlite.connect(DB_PATH) as db:
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    await db.commit()

@app.get("/notes") # registers this function as the GET /notes endpoint
async def list_notes():
    async with aiosqlite.connect(DB_PATH) as db: # opens a connection to the SQLite file
        db.row_factory = aiosqlite.Row # makes rows behave like dicts instead of plain tuples
        async with db.execute("SELECT * FROM notes") as cursor: 
            rows = await cursor.fetchall() # fetches all result rows into memory
    return [dict(row) for row in rows] # converts each row to a plain dict so FastAPI can serialize it to JSON
