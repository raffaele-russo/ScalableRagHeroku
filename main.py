from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from rag import rag
from worker import generate_response, celery_app
import uuid
from celery.result import AsyncResult

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/invoke")
async def invoke(request: Request):
    try:
        request_data = await request.json()
        user_input = request_data.get("input")  # Get the 'input' field from the request data
        print("User input:", user_input)

        # Invoke the RAG model with the user's input
        if user_input:
            task_id = str(uuid.uuid4())
            print("Adding response task to the queue")
            generate_response.apply_async(args=[user_input], task_id=task_id)
            return JSONResponse(content={"task_id": task_id})
        else:
            print("No user input")
            response_message = {
                "error": "Please ask a question",
                "context": []
            }
            return JSONResponse(content=response_message, status_code=400)  # Returning a 400 for invalid request
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Something went wrong"}, status_code=500)

@app.get("/check_task/{task_id}")
async def check_task(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    if result.ready():
        if result.successful():
            if result.result.get("error"):
                return {"status": "failed", "error": "Something went wrong"}
            return {"status": "completed", "llm_response": result.result}
        else:
            return {"status": "failed", "error": "Something went wrong"}
    else:
        return {"status": "pending"}