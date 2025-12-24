"""
LaTeX to PDF Converter - Legacy entry point
This file now imports from the new modular structure in src/
"""

from src.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
