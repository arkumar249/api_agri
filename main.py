from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env vars
load_dotenv()



logging.basicConfig(
    level=logging.INFO,  # Show INFO and above
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# print(supabase.table("users").select("*").execute())
# Logger
logger = logging.getLogger("my")

# FastAPI app
app = FastAPI(title="Chat API")
logger.info(" FastAPI server started")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from routers import users, chats, auth
app.include_router(users.router)
app.include_router(chats.router)
logger.info("Test logger from auth.py")
app.include_router(auth.router)

# Root route
@app.get("/")
async def root():
    return {"message": "Hello World"}
