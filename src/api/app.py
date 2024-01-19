from fastapi import FastAPI

from api.routers.test import router as test_router

app = FastAPI(title="API", root_path="")
app.include_router(test_router, tags=["Test"])
