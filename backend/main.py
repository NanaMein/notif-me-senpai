from fastapi import FastAPI, status


app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    print("RUNNING UVICORN")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
