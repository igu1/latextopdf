from src.config import HOST, PORT
from src.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
