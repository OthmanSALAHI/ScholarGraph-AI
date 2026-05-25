from fastapi import APIRouter

router = APIRouter()


@router.get("")
def get_graph() -> dict[str, list[dict[str, str]]]:
    return {"nodes": [], "edges": []}