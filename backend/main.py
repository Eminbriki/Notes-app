from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = sqlite3.connect("modules.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    goal TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    progress INTEGER NOT NULL,
    notes TEXT,
    passed INTEGER NOT NULL
)
""")
conn.commit()

class Module(BaseModel):
    name: str
    goal: str
    exam_date: str
    progress: int
    notes: str
    passed: bool

@app.get("/")
def root():
    return {"message": "Semester Module Tracker API is running"}

@app.get("/modules")
def get_modules():
    cursor.execute("SELECT id, name, goal, exam_date, progress, notes, passed FROM modules")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "goal": row[2],
            "exam_date": row[3],
            "progress": row[4],
            "notes": row[5],
            "passed": bool(row[6]),
        })

    return result

@app.post("/modules")
def create_module(module: Module):
    cursor.execute(
        "INSERT INTO modules (name, goal, exam_date, progress, notes, passed) VALUES (?, ?, ?, ?, ?, ?)",
        (
            module.name,
            module.goal,
            module.exam_date,
            module.progress,
            module.notes,
            int(module.passed),
        ),
    )
    conn.commit()
    return {"message": "Module added successfully"}

@app.put("/modules/{module_id}")
def update_module(module_id: int, module: Module):
    cursor.execute(
        """
        UPDATE modules
        SET name = ?, goal = ?, exam_date = ?, progress = ?, notes = ?, passed = ?
        WHERE id = ?
        """,
        (
            module.name,
            module.goal,
            module.exam_date,
            module.progress,
            module.notes,
            int(module.passed),
            module_id,
        ),
    )
    conn.commit()
    return {"message": f"Module {module_id} updated successfully"}

@app.delete("/modules/{module_id}")
def delete_module(module_id: int):
    cursor.execute("DELETE FROM modules WHERE id = ?", (module_id,))
    conn.commit()