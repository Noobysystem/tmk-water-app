import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import json

app = FastAPI(title="TMK Water Network App - PV")

# Создаем папки при старте
os.makedirs("data", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

DB_FILE = "data/drinking_network.json"
LANDMARKS_FILE = "frontend/landmarks_pv.json"

class Node(BaseModel):
    id: str
    name: str
    type: str  # 'valve' или 'hydrant'
    status: str # 'open', 'closed', 'no_cheeks', 'hard_turn', 'jammed_closed'
    description: str = ""
    diameter: int = 150
    x: float
    y: float

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Если базы нет, пробуем подтянуть из извлеченного DXF
    dxf_path = "data/dxf_extracted_nodes.json"
    if os.path.exists(dxf_path):
        with open(dxf_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {"nodes": data.get("nodes", []), "dimensions": {"width": 9946, "height": 7029}}
    return {"nodes": [], "dimensions": {"width": 9946, "height": 7029}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Автоматический бэкап в storage при изменении
    os.makedirs("storage", exist_ok=True)
    shutil.copy(DB_FILE, "storage/drinking_network_backup.json")

@app.get("/api/drinking/network")
def get_network():
    db = load_db()
    # Гарантируем правильные размеры под новую HD картинку 9946x7029
    db["dimensions"] = {"width": 9946, "height": 7029}
    return db

@app.post("/api/drinking/node")
def add_node(node: Node):
    db = load_db()
    db["nodes"].append(node.dict())
    save_db(db)
    return {"status": "success", "id": node.id}

@app.put("/api/drinking/node/{node_id}")
def update_node(node_id: str, node: Node):
    db = load_db()
    updated = False
    for i, n in enumerate(db["nodes"]):
        if n["id"] == node_id:
            db["nodes"][i] = node.dict()
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Node not found")
    save_db(db)
    return {"status": "success"}

@app.delete("/api/drinking/node/{node_id}")
def delete_node(node_id: str):
    db = load_db()
    db["nodes"] = [n for n in db["nodes"] if n["id"] != node_id]
    save_db(db)
    return {"status": "success"}

@app.get("/api/drinking/export")
def export_db():
    if os.path.exists(DB_FILE):
        return FileResponse(DB_FILE, media_type="application/json", filename="drinking_network_backup.json")
    raise HTTPException(status_code=404, detail="Database not found")

@app.post("/api/drinking/import")
async def import_db(file: UploadFile = File(...)):
    contents = await file.read()
    with open(DB_FILE, "wb") as f:
        f.write(contents)
    db = load_db()
    return {"status": "success", "count": len(db.get("nodes", []))}

# Раздаем статику фронтенда
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
