from fastapi import FastAPI

app = FastAPI()

@app.post("/identify")
async def identify():
    return {"message": "Identify!"}

@app.get("/")
async def root():
    return {"message": "Hello World!"}

