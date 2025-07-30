import os
import sys


def create_project_cli():
    if len(sys.argv) < 2:
        print("❌ Usage: your-cli-command <project_name>")
        sys.exit(1)
    create_project(sys.argv[1])


def create_project(project_name):
    base = os.path.abspath(project_name)
    app_path = os.path.join(base, "app")

    os.makedirs(app_path, exist_ok=True)

    apps = ["user", "account"]
    for app_name in apps:
        app_dir = os.path.join(app_path, app_name)
        forms_dir = os.path.join(app_dir, "forms")
        os.makedirs(forms_dir, exist_ok=True)
        with open(os.path.join(app_dir, "__init__.py"), "w"): pass
        with open(os.path.join(forms_dir, "__init__.py"), "w"): pass
        with open(os.path.join(app_dir, "route.py"), "w") as f:
            f.write(f"""from fastapi import APIRouter

{app_name}_router = APIRouter()

@{app_name}_router.get("/ping")
def ping():
    return {{"message": "{app_name} pong"}}
""")

    os.makedirs(os.path.join(app_path, "websocket"), exist_ok=True)

    common_dir = os.path.join(app_path, "common")
    os.makedirs(common_dir, exist_ok=True)
    with open(os.path.join(common_dir, "comman_function.py"), "w") as f:
        f.write("# Common functions\n")
    with open(os.path.join(common_dir, "common_response.py"), "w") as f:
        f.write("""from fastapi.responses import JSONResponse
import traceback
from fastapi import status, Depends
from fastapi.encoders import jsonable_encoder
import json
import requests
import datetime

# HTTP Success Messages
HEM_INTERNAL_SERVER_ERROR = "Something went wrong. Please try again."
HEM_UNAUTHORIZED = "Your Session has been expired!"
HSM_SUCCESS = "success"

# HTTP Error Messages
HEM_ERROR = "error"
HEM_INVALID_EMAIL_FORMAT = "Invalid email format"
HEM_INVALID_MOBILE_FORMAT = "Invalid mobile number format"
HEM_INVALID_VERIFY_CODE_FORMAT = "Verify code must contain only numbers."

def successResponse(status_code, msg, data={{}}):
    return JSONResponse(
        status_code=status_code,
        content={{
            "status": "success",
            "message": msg,
            "data": data,
        }}
    )

def errorResponse(status_code, msg, data={{}}):
    return JSONResponse(
        status_code=status_code,
        content={{
            "status": "error",
            "message": msg,
            "data": data,
        }}
    )
""")

    shared_dir = os.path.join(app_path, "shared")
    os.makedirs(shared_dir, exist_ok=True)
    with open(os.path.join(shared_dir, "__init__.py"), "w"): pass
    with open(os.path.join(shared_dir, "db.py"), "w") as f:
        f.write("# DB connection code\n")

    with open(os.path.join(app_path, "main.py"), "w") as f:
        f.write("""\"\"\"
Main module of exchange backend.
\"\"\"
import os
import pathlib
import logging
import uvicorn
from app.account.route import account_router
from customized_log import CustomizeLogger
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException, Security

\"\"\"
code for save logs in customise path
\"\"\"
logger = logging.getLogger(__name__)
module_path = str(pathlib.Path(__file__).parent.absolute())
config_path = str(os.path.join(module_path, "config", "logging_config.json"))

def create_app() -> FastAPI:
    app = FastAPI(title=' demo | demo API', debug=False)
    logger = CustomizeLogger.make_logger(config_path)
    app.logger = logger
    app.include_router(account_router)
    return app

app = create_app()

origins = [
    "*"
    # "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, port=8060, ws_ping_interval=1, ws_ping_timeout=-1)
""")

    print(f"✅ Project '{project_name}' generated successfully!")
