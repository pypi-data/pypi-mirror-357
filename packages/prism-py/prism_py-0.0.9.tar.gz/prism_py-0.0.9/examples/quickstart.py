# examples/quickstart.py
import os
import uvicorn
from fastapi import FastAPI
from prism.db.client import DbClient
from prism.prism import ApiPrism

# 1. Load Database Configuration from Environment
db_url = os.getenv(
    "DATABASE_URL", "postgresql://a_hub_admin:password@localhost:5432/a_hub"
)
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set.")

# 2. Initialize FastAPI and Prism
# Create the main FastAPI app.
app = FastAPI(
    title="Prism-py Auto-Generated API",
    description="A powerful REST API created directly from a database schema.",
    version="1.0.0",
)

# Initialize the Prism orchestrator.
api_prism = ApiPrism(db_client=DbClient(db_url=db_url), app=app)

# 3. Generate All API Routes
api_prism.gen_all_routes()

# 4. Run the Server
if __name__ == "__main__":
    # Log connection stats and a welcome message before starting the server.
    api_prism.db_client.log_connection_stats()
    api_prism.print_welcome_message(host="127.0.0.1", port=8000)

    print(f"🚀 Starting server at http://127.0.0.1:8000")
    print("   Access API docs at http://127.0.0.1:8000/docs")
    print("   Press CTRL+C to stop.")
    uvicorn.run("__main__:app", host="127.0.0.1", port=8000, reload=True)
