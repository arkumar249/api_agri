from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID



router = APIRouter(prefix="/auth", tags=["auth"])
