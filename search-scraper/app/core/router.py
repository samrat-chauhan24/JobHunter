# app/core/router.py

from app.providers.wellfound import search_wellfound
from app.providers.hirist import search_hirist
from app.providers.naukri import search_naukri
from app.providers.internshala import search_internshala

PROVIDERS = {

    "Wellfound": search_wellfound,

    "Hirist": search_hirist,
    
    "Naukri": search_naukri,

    "Internshala": search_internshala,

}

async def search_provider(data):

    provider = data["provider"]

    if provider not in PROVIDERS:
        return {

            "status": "FAILED",

            "error": f"Unknown provider '{provider}'"

        }

    return await PROVIDERS[provider](data)