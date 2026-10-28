from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import database as db, ai_service as ai

app = FastAPI(title="FoodVerse AI")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
db.init_db()

MAX_MB = 20

async def _read(f: UploadFile):
    data = await f.read()
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"File {MAX_MB}MB se chhoti honi chahiye")
    return data, f.content_type or "application/octet-stream"

def _guard(fn):
    try:
        return fn()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"AI error: {e}")

@app.get("/api/health")
def health():
    return {"status": "ok", "demo_mode": ai.DEMO, "model": ai.MODEL}

async def _single(kind, prompt, file):
    data, mime = await _read(file)
    result = _guard(lambda: ai.run(kind, prompt, [(data, mime)]))
    result["_id"] = db.save(kind, file.filename, result)
    return result

@app.post("/api/analyze/nutrition")
async def nutrition(file: UploadFile = File(...)):
    return await _single("nutrition", ai.nutrition_prompt(), file)

@app.post("/api/analyze/freshness")
async def freshness(file: UploadFile = File(...)):
    return await _single("freshness", ai.freshness_prompt(), file)

@app.post("/api/analyze/hygiene")
async def hygiene(file: UploadFile = File(...)):
    return await _single("hygiene", ai.hygiene_prompt(), file)

@app.post("/api/cooking")
async def cooking(query: str = Form(""), ingredients: str = Form(""), file: Optional[UploadFile] = File(None)):
    files, name = [], query or "cooking"
    if file is not None and file.filename:
        files.append(await _read(file)); name = file.filename
    result = _guard(lambda: ai.run("cooking", ai.cooking_prompt(query, ingredients), files))
    result["_id"] = db.save("cooking", name, result)
    return result

class Profile(BaseModel):
    age: int = 25
    gender: str = "male"
    weight: float = 65
    height: float = 170
    goal: str = "maintain weight"
    diet: str = "vegetarian"
    allergies: str = ""
    cuisine: str = "Indian"
    days: int = 3

@app.post("/api/meal-plan")
def meal_plan(p: Profile):
    result = _guard(lambda: ai.run("mealplan", ai.mealplan_prompt(p.model_dump())))
    result["_id"] = db.save("mealplan", f"{p.goal} / {p.diet}", result)
    return result

@app.get("/api/history")
def history():
    return db.list_all()

@app.delete("/api/history/{item_id}")
def delete_history(item_id: int):
    db.delete(item_id)
    return {"deleted": item_id}
