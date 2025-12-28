Local Run Instructions:

    BE:
        cd server
        source .venv/bin/activate
        uvicorn main:app --reload --port 8000

        browser: http://localhost:8000/health
        docs: http://localhost:8000/docs