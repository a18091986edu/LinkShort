from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def index():
    return {"status": "it's alive"}
