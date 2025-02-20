from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers.chat import chat_router

app = FastAPI()
app.include_router(chat_router)

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
