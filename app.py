from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from predict_logic import PREDICTOR
import uvicorn
import asyncio
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Banana Ripeness Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict", response_model=Dict[str, Any])
async def predict_ripeness(file: UploadFile = File(...)):
    if not PREDICTOR:
        raise HTTPException(status_code=503, detail="Model service not ready.")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        image_bytes = await file.read()
        # Run prediction in a thread pool to avoid blocking the event loop
        prediction_result = await asyncio.to_thread(PREDICTOR.predict, image_bytes)
        return JSONResponse(content=prediction_result, status_code=200)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)