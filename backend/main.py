# from dotenv import load_dotenv

# # Load environment variables FIRST to ensure they are available for database.py
# load_dotenv() 

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from routers import auth, employees, tasks

# app = FastAPI(title="TaskFlow API", version="1.0.0")

# # CORS (Allow Frontend to talk to Backend)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # The startup event hook that called create_db_and_tables() is removed.
# # MongoDB does not require schema creation on startup.

# # Register Routers
# app.include_router(auth.router)
# app.include_router(employees.router)
# app.include_router(tasks.router)

# @app.get("/")
# def read_root():
#     return {"message": "ProU Backend Running"}

from dotenv import load_dotenv
load_dotenv()   # ensure env vars loaded before other imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import router modules (your files)
from routers.auth import router as auth_router
from routers.employees import router as employees_router
from routers.tasks import router as tasks_router
from routers.requests import router as requests_router

from database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="TaskFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(employees_router)
app.include_router(tasks_router)
app.include_router(requests_router)

# Startup/shutdown hooks
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
def read_root():
    return {"message": "ProU Backend Running"}
