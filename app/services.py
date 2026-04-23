from typing import Dict, Any
from fastapi import HTTPException
from app.database import supabase

def fetch_profiles(
    page: int, 
    limit: int, 
    filters: Dict[str, Any], 
    sort_by: str = "created_at", 
    order: str = "desc"
) -> Dict[str, Any]:
    """Builds and executes the Supabase query based on provided filters."""
    
    if limit > 50:
        limit = 50
        
    offset = (page - 1) * limit
    query = supabase.table("profiles").select("*", count="exact")

    # Apply Filters
    if "gender" in filters: query = query.eq("gender", filters["gender"])
    if "age_group" in filters: query = query.eq("age_group", filters["age_group"])
    if "country_id" in filters: query = query.eq("country_id", filters["country_id"])
    if "min_age" in filters: query = query.gte("age", filters["min_age"])
    if "max_age" in filters: query = query.lte("age", filters["max_age"])
    if "min_gender_probability" in filters: query = query.gte("gender_probability", filters["min_gender_probability"])
    if "min_country_probability" in filters: query = query.gte("country_probability", filters["min_country_probability"])

    is_desc = order == "desc"
    query = query.order(sort_by, desc=is_desc)
    query = query.range(offset, offset + limit - 1)

    try:
        response = query.execute()
        total_count = response.count if response.count is not None else 0
        
        return {
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total_count,
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database query failed")
    