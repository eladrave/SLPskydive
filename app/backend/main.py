from fastapi import FastAPI

# Placeholder app; will be fully bootstrapped in subsequent task
app = FastAPI(title="SLPskydive API")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=8000, reload=True)


