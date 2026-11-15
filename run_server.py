"""
Entry point to run the Paytm ResolveAI Backend Server.
Accessible on 0.0.0.0:8000 (accessible on local network to your teammate).
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
