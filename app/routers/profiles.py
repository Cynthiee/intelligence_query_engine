from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import re
from app.services import fetch_profiles

# Group these endpoints under the /api/profiles prefix
router = APIRouter(prefix="/api/profiles", tags=["Profiles"])

@router.get("")
async def get_profiles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    country_id: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_gender_probability: Optional[float] = None,
    min_country_probability: Optional[float] = None,
    sort_by: str = Query("created_at", pattern="^(age|created_at|gender_probability)$"),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    filters = {}
    if gender: filters["gender"] = gender
    if age_group: filters["age_group"] = age_group
    if country_id: filters["country_id"] = country_id
    if min_age is not None: filters["min_age"] = min_age
    if max_age is not None: filters["max_age"] = max_age
    if min_gender_probability is not None: filters["min_gender_probability"] = min_gender_probability
    if min_country_probability is not None: filters["min_country_probability"] = min_country_probability

    return fetch_profiles(page, limit, filters, sort_by, order)

@router.get("/search")
async def search_profiles(
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Missing or empty parameter")

    query_str = q.lower().strip()
    filters = {}
    
    if "female" in query_str or "females" in query_str: filters["gender"] = "female"
    elif "male" in query_str or "males" in query_str: filters["gender"] = "male"

    if "young" in query_str:
        filters["min_age"], filters["max_age"] = 16, 24
    if "adult" in query_str or "adults" in query_str: filters["age_group"] = "adult"
    elif "teenager" in query_str or "teenagers" in query_str: filters["age_group"] = "teenager"
    elif "child" in query_str or "children" in query_str: filters["age_group"] = "child"
    elif "senior" in query_str or "seniors" in query_str: filters["age_group"] = "senior"

    above_match = re.search(r"above\s+(\d+)", query_str)
    if above_match: filters["min_age"] = int(above_match.group(1))

    below_match = re.search(r"(below|under)\s+(\d+)", query_str)
    if below_match: filters["max_age"] = int(below_match.group(2))

    country_map = {
        "nigeria": "NG", "angola": "AO", "kenya": "KE",
        "benin": "BJ", "ghana": "GH", "south africa": "ZA"
    }
    
    country_match = re.search(r"from\s+([a-z\s]+)", query_str)
    if country_match:
        extracted = country_match.group(1).strip()
        for c_name, c_code in country_map.items():
            if c_name in extracted:
                filters["country_id"] = c_code
                break

    if not filters:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Unable to interpret query"})

    return fetch_profiles(page, limit, filters)
