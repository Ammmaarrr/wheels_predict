"""
Development script to run the FastAPI server with hot reload
"""

import uvicorn
import os

if __name__ == "__main__":
    # Set environment variables for development
    os.environ["ENVIRONMENT"] = "development"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=[".", "../models", "../utils", "../flows", "../data_processing"]
    )
