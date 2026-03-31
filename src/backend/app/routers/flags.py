from fastapi import APIRouter, HTTPException, Query, status

from app.models.flag import FlagResponse
from app.services.flag_cache import flag_cache

router = APIRouter(prefix="/flags", tags=["flags"])

#Receive Random Flag
@router.get(
    "/random",
    response_model=FlagResponse,
    summary="Get a random flag (public)",
    description=(
        "Returns a random country flag that has not been seen in the current session. "
        "Pass the `exclude` parameter with all country codes already shown this round. "
        "No authentication required."
    ),
)
async def get_random_flag(
    exclude: list[str] = Query(default=[], description="Country codes to exclude (already seen this session)"),
) -> FlagResponse:
    flag = flag_cache.random_flag(exclude=set(exclude))
    if flag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unseen flags left. All countries have been shown this session.",
        )
    return FlagResponse(**flag)
