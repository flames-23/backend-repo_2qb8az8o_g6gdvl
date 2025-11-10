import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import VideoProject, AssetRequest

app = FastAPI(title="PromptToTube API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PromptToTube backend running"}

@app.get("/test")
def test_database():
    """Simple DB health check"""
    try:
        collections = db.list_collection_names() if db else []
        return {
            "backend": "✅ Running",
            "database": "✅ Connected" if db else "❌ Not Connected",
            "collections": collections,
        }
    except Exception as e:
        return {
            "backend": "✅ Running",
            "database": f"❌ Error: {str(e)[:120]}",
            "collections": [],
        }

# Utility to convert Mongo docs
class _Doc(BaseModel):
    id: str

    @classmethod
    def from_mongo(cls, doc: dict):
        if not doc:
            return None
        doc = {**doc}
        if "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

@app.post("/api/projects", response_model=dict)
def create_project(payload: AssetRequest):
    try:
        # Build initial project
        project = VideoProject(
            prompt=payload.prompt,
            mode=payload.mode,
            duration_sec=payload.duration_sec,
            language=payload.language,
            voice=payload.voice,
            template=payload.template,
            brand_name=payload.brand_name,
            status="created",
            # Lightweight first version of AI outputs (placeholder deterministic text)
            script=f"Generated {payload.mode} video script for: {payload.prompt}",
            title=f"{payload.prompt[:60]} | PromptToTube",
            tags=["ai", "video", "prompt", payload.mode],
            suggestions=[
                "Trim pauses for tighter pacing",
                "Add your logo to the lower-right corner",
                "Use upbeat background music around 100-120 BPM",
            ],
        )
        inserted_id = create_document("videoproject", project)
        # Read back the document
        doc = db["videoproject"].find_one({"_id": ObjectId(inserted_id)})
        return _Doc.from_mongo(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects", response_model=List[dict])
def list_projects(limit: Optional[int] = 20):
    try:
        docs = get_documents("videoproject", {}, limit)
        return [_Doc.from_mongo(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}", response_model=dict)
def get_project(project_id: str):
    try:
        doc = db["videoproject"].find_one({"_id": ObjectId(project_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Project not found")
        return _Doc.from_mongo(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/projects/{project_id}", response_model=dict)
def update_project(project_id: str, update: dict):
    try:
        update = {k: v for k, v in update.items() if v is not None}
        db["videoproject"].update_one({"_id": ObjectId(project_id)}, {"$set": update})
        doc = db["videoproject"].find_one({"_id": ObjectId(project_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Project not found")
        return _Doc.from_mongo(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
