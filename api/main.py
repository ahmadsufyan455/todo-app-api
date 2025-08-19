from fastapi import FastAPI
from mangum import Mangum

from database import engine
from models import Base
from routers import auth, todos, admin, user

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {
        "app_name": "Todo API",
        "version": "1.0.0",
        "description": "A FastAPI backend for managing todos with authentication and role-based access.",
        "author": "FYN",
        "docs_url": "/docs",
        "endpoints": {
            "health_check": "/healthy",
            "auth": "/auth/*",
            "todos": "/todos/*",
            "admin": "/admin/*",
            "users": "/users/*"
        }
    }


@app.get("/healthy")
async def healthy():
    return {"message": "healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)

mangum = Mangum(app)
