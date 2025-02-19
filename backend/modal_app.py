import modal
import sys
import os

# Add the backend directory to the Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your FastAPI app
from app.main import app as fastapi_app

# Create a Modal App instance
app = modal.App("backend-fastapi-app")

# Define the container image with environment variables and dependencies
image = (
    modal.Image.debian_slim()
    .env({
        "DATABASE_URL": "postgresql+asyncpg://database1_owner:S2JlkK3yWdaU@ep-restless-unit-a1yyl0fh.ap-southeast-1.aws.neon.tech/database1?ssl=true",
        "NEWSAPI_KEY": "3382203206d74dab95d0d09077a28a56",
        "TRANSFORMERS_CACHE": "/tmp",
    })
    .pip_install(
        "fastapi==0.100.0",
        "uvicorn[standard]==0.34.0",
        "sqlalchemy>=1.4.0",
        "asyncpg>=0.25.0",
        "python-dotenv==1.0.1",
        "passlib[bcrypt]==1.7.4",
        "requests==2.32.3",
        "tweepy==4.15.0",
        "transformers==4.48.3",
        "torch==2.6.0",
        "datasets==3.2.0",
        "langchain>=0.0.200",
        "langchain-community>=0.0.20",
        "pydantic[email]>=2.0.2,<3.0.0",
        "mangum==0.17.0",
        "email-validator>=1.0.0"
    )
    # Add local Python modules to address deprecation warning
    .add_local_python_source("app")
    .add_local_python_source("_remote_module_non_scriptable")
    # Use add_local_dir instead of Mount
    .add_local_dir("./app", remote_path="/root/app")
)

# Create the FastAPI endpoint
@app.function(
    image=image,
    gpu="a100",  # or "h100" depending on availability
    timeout=60 * 10  # 10 minutes timeout
)
@modal.asgi_app()
def web():
    return fastapi_app