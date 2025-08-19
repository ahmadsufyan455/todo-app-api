from fastapi import FastAPI

from database import engine
from models import Base
from routers import auth, todos, admin, user
from mangum import Mangum

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/healthy")
async def healthy():
    return {"message": "healthy"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)

mangum = Mangum(app)
