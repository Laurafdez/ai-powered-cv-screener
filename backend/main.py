from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import upload, chat
from config.settings import API_HOST, API_PORT

app = FastAPI(title="CV Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "CV Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
