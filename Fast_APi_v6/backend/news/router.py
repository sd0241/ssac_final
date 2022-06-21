from fastapi.routing import APIRouter

memo_router = APIRouter()

@memo_router.get("/test")
async def test():
    return {"say":"hello"}