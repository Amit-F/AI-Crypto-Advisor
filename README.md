Local Run Instructions:

    BE:
        cd server
        source .venv/bin/activate
        uvicorn main:app --reload --port 8000

        browser url: http://localhost:8000/health
        docs url: http://localhost:8000/docs

    FE:
        cd client
        npm run dev

        VITE url: http://localhost:5173