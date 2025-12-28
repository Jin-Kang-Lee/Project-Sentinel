import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.workflows.orchestrator import app as sentinel_app

app = FastAPI(title="Project Sentinel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_path = tmp.name
            tmp.write(await file.read())

        result = sentinel_app.invoke({"pdf_path": temp_path})

        return {
            "final_decision": result.get("final_decision"),
            "risk_analysis": result.get("risk_analysis"),
            "legal_opinion": result.get("legal_opinion"),
            "wealth_plan": result.get("wealth_plan"),
            "client_data": result.get("client_data"),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
