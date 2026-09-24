from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FinSight AI Backend is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}