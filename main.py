import uvicorn
from fastapi import APIRouter, FastAPI

from api.handlers.audio_handlers import audio_router
from api.handlers.user_handlers import user_router


app = FastAPI(title="Bewise_task_2")

main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user")
main_api_router.include_router(audio_router, prefix="/record")

app.include_router(main_api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
