from fastapi import APIRouter, HTTPException, status, Response, Request
from uuid import UUID
from schemas.user import UserCreate, UserLogin, UserOut
from core.database import supabase
from utilities.auth_utils import hash_password, verify_password, create_refresh_token, decode_token


from main import logger

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate):
    # Check if email already exists
    exists = supabase.table("users").select("*").eq("email", user.email).execute()
    if exists.data and len(exists.data) > 0:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user.password)

    # Insert into Supabase
    row = supabase.table("users").insert({
        "user_name": user.full_name,
        "email": user.email,
        "hashed_password": hashed_pw,
        "role": user.role
    }).execute()

    if not row.data:
        raise HTTPException(status_code=500, detail="Failed to create user")

    user_data = row.data[0]
    return {
        "userid": user_data["id"],
        "full_name": user_data["user_name"],
        "email": user_data["email"],
        "role": user_data["role"]
    }


@router.post("/login")
async def login(user: UserLogin, response: Response):
    row = supabase.table("users").select("*").eq("email", user.email).execute()

    if not row.data or len(row.data) == 0:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_data = row.data[0]

    # Verify password
    if not verify_password(user.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate refresh token
    refresh_token = create_refresh_token({"sub": str(user_data["id"])})

    # Set cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
           # in prod
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )

    return {"message": "Login successful"}


@router.get("/me")
async def get_me(request: Request):
    token = request.cookies.get("refresh_token")
    logger.info("Test logger from /me route")
    # payload = decode_token(token)
    # return payload.get("sub")
    
    
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    payload = decode_token(token)
    logger.info(f"My variable value: {payload}")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    logger.info(f"My variable value: {payload}")

    id = payload.get("sub")

    # row = supabase.table("users").select("id , user_name, email, role").eq("id", id).execute()
    row= supabase.table("users").select("id ,  user_name , email , role").eq("id" , id).execute()
    # return row

   
    if not row.data:
        raise HTTPException(status_code=404, detail="User not found")

    return row.data[0]



@router.get("/hi")
async def hi():
    return supabase.table("users").select("*").execute().data