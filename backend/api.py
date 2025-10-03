from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "yay! API is working!"}

@app.post("/improve")
def improve(prompt: dict):
    original = prompt["prompt"]
    improved = f"Make it clearer: {original}"
    return {"improved_prompt": improved}