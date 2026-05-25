from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_summaries() -> dict[str, list[dict[str, str]]]:
    return {"summaries": []}