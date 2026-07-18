# app/api/routes.py

from fastapi import APIRouter

from app.models.search_request import SearchRequest
from app.core.router import search_provider

router = APIRouter()


@router.post("/search")
async def search(request: SearchRequest):

    return await search_provider(
        request.model_dump()
    )