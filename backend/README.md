# Bellul Week 3 - FastAPI Backend

Simple API service for prompt improvement.

## How to run:

1. Install dependencies:

   ```bash
   pip install -r requirements.txt

2. Install dependencies:

   ```bash
   uvicorn api:app --reload



3. Open your browser to: http://127.0.0.1:8000

## What it does: 

What it does:

- GET / → Just a quick check to see if the API is up and running
- POST /improve → You send in a piece of text (a "prompt") and the API sends back a better version
- Built-in docs at http://127.0.0.1:8000/docs - let you test everything in your browser