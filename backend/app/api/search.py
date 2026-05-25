from fastapi import APIRouter

router = APIRouter()


@router.get("")
def search_papers() -> dict[str, list[dict[str, str]]]:
    return {"results": []}