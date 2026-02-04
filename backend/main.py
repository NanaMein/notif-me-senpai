from fastapi import FastAPI, status, HTTPException
from routers.v1 import router


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    print("RUNNING UVICORN")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

