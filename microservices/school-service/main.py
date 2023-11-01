from fastapi import FastAPI, APIRouter
import httpx
import uvicorn

# from register_service import register

from utils import register_to_consul

fake_dbs = [
    {"name": "SD 1", "id": 1},
    {"name": "SD 2", "id": 2}
]

app = FastAPI()

router = APIRouter()


@app.on_event("startup")
def startup():
    # register()
    register_to_consul()


@router.get("/")
async def get_school_list():
    return fake_dbs


@router.get("/detail/{school_id}")
async def get_school_detail(school_id: int):
    school = filter(lambda x: x.get("id") == school_id, fake_dbs)
    students = {}
    students = await client.get(f"http://student_service/school/{school_id}/")
    students = students.json()

    ret = {
        "school": school,
        "students": students
    }
    return students


@router.get("/health")
def health_status():
    return {"status": "healthy"}


@router.get("/register-to-consul")
async def register_to_consul_manually():
    return register_to_consul()


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8095)
