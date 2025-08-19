from fastapi import FastAPI
from mangum import Mangum

from database import engine
from models import Base
from routers import auth, todos, admin, user

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
async def about():
    return {
        "app_name": "To-Do App",
        "version": "0.0.1",
        "author": "Fyn",
        "status": "healthy"
    }


@app.get("/healthy")
async def healthy():
    return {"message": "healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)

mangum = Mangum(app)
