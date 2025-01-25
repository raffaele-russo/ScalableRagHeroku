from celery import Celery
from dotenv import load_dotenv
from rag import rag
import os

load_dotenv()
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
celery_app = Celery('tasks', broker=REDIS_URL, backend = REDIS_URL)  


@celery_app.task
def generate_response(user_input):
    try:
        print("Worker starting...")
        print("Invoking...") 
        result = rag.invoke(user_input)

        # Process the 'context' documents into a cleaner response
        context = result.get("context", [])
        
        # Create a list of context items, each containing metadata and page content
        context_details = []
        for doc in context:
            context_details.append({
                "page_content": doc.page_content,
                "page": doc.metadata.get("page", "Unknown Page")
            })

        # Get the answer
        answer = result.get("answer", "Sorry, I couldn't find an answer.")
        
        # Return the structured response
        response_message = {
            "answer": answer,
            "context": context_details
        }
        return response_message
    except Exception as e:
        return {"error": "An error occurred while processing the request."}