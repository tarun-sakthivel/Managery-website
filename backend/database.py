# # import os
# # from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

# # # Configuration relies on environment variables (loaded in main.py)
# # # NOTE: MONGO_URI and MONGO_DATABASE_NAME must be set in your environment variables/config.
# # MONGO_URI = os.getenv("MONGO_URI")
# # MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")
# # EMPLOYEE_COLLECTION_NAME = "employees" # Collection name for users/employees

# # if not MONGO_URI:
# #     # Crucial check: the application cannot start without the URI
# #     raise ValueError("MONGO_URI environment variable not set. Please check your environment.")

# # # Global variables for the client and database instance
# # client: AsyncIOMotorClient = None
# # db: AsyncIOMotorDatabase = None

# # async def connect_to_mongo():
# #     """
# #     Initializes the MongoDB client and database connection.
# #     This function should be called during FastAPI startup events.
# #     """
# #     global client, db
# #     try:
# #         print(f"Connecting to MongoDB...")
# #         # Use serverSelectionTimeoutMS to prevent indefinite blocking
# #         client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
# #         # Test connection by trying a lightweight command
# #         await client.admin.command('ping') 
        
# #         db = client[MONGO_DATABASE_NAME]
# #         print(f"Successfully connected to MongoDB database: {MONGO_DATABASE_NAME}")
        
# #     except Exception as e:
# #         print(f"Failed to connect to MongoDB. Error: {e}")
# #         # Raise the exception to fail startup if connection cannot be established
# #         raise

# # async def close_mongo_connection():
# #     """
# #     Closes the MongoDB client connection.
# #     This function should be called during FastAPI shutdown events.
# #     """
# #     global client
# #     if client:
# #         print("Closing MongoDB connection.")
# #         client.close()

# # # --- Dependency Injectors (Used in routers) ---

# # async def user_collection_dependency() -> AsyncIOMotorCollection:
# #     """Dependency for accessing the employee/user collection (used in auth.py)."""
# #     if db is None:
# #         raise Exception("Database connection not established. Ensure connect_to_mongo was called.")
# #     return db[EMPLOYEE_COLLECTION_NAME]

# # async def task_collection_dependency() -> AsyncIOMotorCollection:
# #     """Dependency for accessing the tasks collection."""
# #     if db is None:
# #         raise Exception("Database connection not established.")
# #     return db["tasks"]

# # async def changerequest_collection_dependency() -> AsyncIOMotorCollection:
# #     """Dependency for accessing the change requests collection."""
# #     if db is None:
# #         raise Exception("Database connection not established.")
# #     return db["change_requests"]

# import os
# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
# from typing import Optional

# # Configuration relies on environment variables (loaded in main.py)
# # NOTE: MONGO_URI and MONGO_DATABASE_NAME must be set in your environment variables/config.
# MONGO_URI = os.getenv("MONGO_URI")
# MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")
# EMPLOYEE_COLLECTION_NAME = "employees" # Collection name for users/employees

# if not MONGO_URI:
#     # Crucial check: the application cannot start without the URI
#     raise ValueError("MONGO_URI environment variable not set. Please check your environment.")

# # Global variables for the client and database instance
# client: Optional[AsyncIOMotorClient] = None
# db: Optional[AsyncIOMotorDatabase] = None

# async def connect_to_mongo():
#     """
#     Initializes the MongoDB client and database connection.
#     This function should be called during FastAPI startup events.
#     """
#     global client, db
#     try:
#         print("Connecting to MongoDB...")
#         # Use serverSelectionTimeoutMS to prevent indefinite blocking
#         client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
#         # Test connection by trying a lightweight command
#         await client.admin.command('ping') 
        
#         db = client[MONGO_DATABASE_NAME]
#         print(f"Successfully connected to MongoDB database: {MONGO_DATABASE_NAME}")
        
#     except Exception as e:
#         print(f"Failed to connect to MongoDB. Error: {e}")
#         # Raise the exception to fail startup if connection cannot be established
#         raise

# async def close_mongo_connection():
#     """
#     Closes the MongoDB client connection.
#     This function should be called during FastAPI shutdown events.
#     """
#     global client
#     if client:
#         print("Closing MongoDB connection.")
#         client.close()

# # --- Dependency Injectors (Used in routers) ---

# async def user_collection_dependency() -> AsyncIOMotorCollection:
#     """Dependency for accessing the employee/user collection (used in auth.py)."""
#     if db is None:
#         # Raise a 503 error if the DB isn't connected (shouldn't happen with startup events)
#         raise Exception("Database connection not established. Ensure connect_to_mongo was called.")
#     return db[EMPLOYEE_COLLECTION_NAME]

# async def task_collection_dependency() -> AsyncIOMotorCollection:
#     """Dependency for accessing the tasks collection."""
#     if db is None:
#         raise Exception("Database connection not established.")
#     return db["tasks"]

# async def changerequest_collection_dependency() -> AsyncIOMotorCollection:
#     """Dependency for accessing the change requests collection."""
#     if db is None:
#         raise Exception("Database connection not established.")
#     return db["change_requests"]

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Optional

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "testdb")
EMPLOYEE_COLLECTION_NAME = "employees"

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set. Please set it (e.g. in .env).")

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def connect_to_mongo():
    global client, db
    try:
        print("Connecting to MongoDB...")
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # quick ping to ensure connection (raises if not reachable)
        await client.admin.command("ping")
        db = client[MONGO_DATABASE_NAME]
        print(f"Connected to MongoDB database: {MONGO_DATABASE_NAME}")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    global client
    if client:
        print("Closing MongoDB connection...")
        client.close()
        client = None

# --- Dependency injectors ---
async def user_collection_dependency() -> AsyncIOMotorCollection:
    if db is None:
        raise Exception("Database not connected. Ensure connect_to_mongo() ran on startup.")
    return db[EMPLOYEE_COLLECTION_NAME]

async def task_collection_dependency() -> AsyncIOMotorCollection:
    if db is None:
        raise Exception("Database not connected.")
    return db["tasks"]

async def changerequest_collection_dependency() -> AsyncIOMotorCollection:
    if db is None:
        raise Exception("Database not connected.")
    return db["change_requests"]
