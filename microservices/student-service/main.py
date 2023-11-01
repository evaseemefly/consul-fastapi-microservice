from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()


@router.get("/")
async def hello():
    return {"message": "Hello, FastAPI!"}


@router.get("/greet/{name}")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8095)
