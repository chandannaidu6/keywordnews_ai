import modal
from app.main import app  
stub = modal.Stub("backend-fastapi-app")

image = modal.Image.debian().pip_install(
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
)

@stub.asgi_app(image=image)
def fastapi_app():
    return app

if __name__ == "__main__":
    stub.deploy("backend-fastapi-app")
