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

Entity-Relationship Diagram
  USERS ||--o| PREFERENCES : has
  USERS ||--o{ DASHBOARD_ITEMS : has
  USERS ||--o{ VOTES : casts
  DASHBOARD_ITEMS ||--o{ VOTES : receives

  USERS {
    int id PK
    string email "UNIQUE, indexed"
    string name
    string password_hash
    datetime created_at
  }

  PREFERENCES {
    int user_id PK, FK "-> USERS.id"
    json assets
    string investor_type
    json content_types
    datetime created_at
    datetime updated_at
  }

  DASHBOARD_ITEMS {
    int id PK
    int user_id FK "-> USERS.id"
    date date "indexed"
    string item_type "news|prices|ai|meme"
    json payload
    datetime created_at
  }

  VOTES {
    int id PK
    int user_id FK "-> USERS.id"
    int dashboard_item_id FK "-> DASHBOARD_ITEMS.id"
    int value "+1/-1"
    datetime created_at
  }
