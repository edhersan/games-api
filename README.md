# Games API

API REST construida con FastAPI para consultar información de juegos almacenada en MongoDB.

## Requisitos
- Python 3.11+
- MongoDB

## Configuración
1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Crea un archivo `.env` basado en `.env.example`:
   - `MONGODB_URL`
   - `MONGODB_DB_NAME`

## Ejecución local
```bash
uvicorn app.main:app --reload
```

## Endpoints principales
- `GET /health` → estado del servicio
- `GET /ping` → prueba rápida
- `GET /games` → lista con los nombres de todos los juegos
- `GET /games/{identifier}` → juego completo por ObjectId o título
- `GET /games/{identifier}/art` → arte del juego
- `GET /games/{identifier}/info` → información descriptiva

## Documentación interactiva
- Swagger: `/docs`
- ReDoc: `/redoc`
