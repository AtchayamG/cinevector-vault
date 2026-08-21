import uvicorn
import os
from app.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", settings.PORT))
    host = os.getenv("HOST", settings.HOST)
    print(f"Starting {settings.PROJECT_NAME} on {host}:{port}...")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
