"""
SimpleAgent - Application Entry Point
Run this file to start the SimpleAgent server
"""

import uvicorn

if __name__ == "__main__":
    print("\n" + "="*50)
    print("SimpleAgent Server Starting...")
    print("="*50)
    print("\nAccess the application at:")
    print("  - http://localhost:8000")
    print("  - http://127.0.0.1:8000")
    print("\nPress CTRL+C to stop the server")
    print("="*50 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host="localhost",  # Bind to localhost only
        port=8000,
        reload=True
    )


