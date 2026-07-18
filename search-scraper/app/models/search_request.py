# app/models/search_request.py

from pydantic import BaseModel


class SearchRequest(BaseModel):

    requestId: str

    createdAt: str

    status: str

    provider: str

    providerType: str

    keyword: str

    location: str

    experience: str

    remote: str

    jobType: str