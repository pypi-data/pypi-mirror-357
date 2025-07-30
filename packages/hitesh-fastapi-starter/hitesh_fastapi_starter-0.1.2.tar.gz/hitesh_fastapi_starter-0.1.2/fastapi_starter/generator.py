import os
import sys

TEMPLATE = {
    "main.py": '''from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI Starter!"}
''',
    "api/routes.py": '''from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping():
    return {"ping": "pong"}
''',
    "models/models.py": '''# Your Pydantic models will go here
'''
}

def create_fastapi_project(project_name):
    base_path = os.path.join(os.getcwd(), project_name)
    os.makedirs(base_path, exist_ok=True)

    os.makedirs(os.path.join(base_path, "api"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "models"), exist_ok=True)

    with open(os.path.join(base_path, "main.py"), "w") as f:
        f.write(TEMPLATE["main.py"])

    with open(os.path.join(base_path, "api", "routes.py"), "w") as f:
        f.write(TEMPLATE["api/routes.py"])

    with open(os.path.join(base_path, "models", "models.py"), "w") as f:
        f.write(TEMPLATE["models/models.py"])

    print(f"✅ FastAPI starter project '{project_name}' created!")

def create_fastapi_project_cli():
    if len(sys.argv) < 2:
        print("❌ Usage: fastapi-starter <project_name>")
        sys.exit(1)
    create_fastapi_project(sys.argv[1])
