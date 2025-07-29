
# 🔥 Phoenix AI Services

Unified agentic framework to run dynamic RAG APIs and utility tools like calculator, date, and python evaluator.

## 🔧 Setup

```bash
poetry install
poetry run python phoenix_ai_services/main.py
```

## 🚀 API Endpoints

### RAG
- `POST /rag/endpoints/{name}` – Register RAG
- `PUT /rag/endpoints/{name}` – Update RAG
- `DELETE /rag/endpoints/{name}` – Remove RAG
- `GET /rag/query/{name}` – Ask RAG agent

### Tools
- `GET /tool/calculator?input_data=2+3*4`
- `GET /tool/system_time`
- `GET /tool/python?input_data=round(3.14159, 2)`

### Admin
- `GET /registry` – View all registered endpoints

## 🧠 Powered by Phoenix Agentic AI Framework
