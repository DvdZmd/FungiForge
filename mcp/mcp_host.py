from modelcontext.host import Host, Schema, Function
from modelcontext.types import String
from fastapi import FastAPI
import uvicorn

from server.routes import camera_routes  # adjust to your actual import

# 1. Define a simple MCP function (we'll start with something basic)
@Function()
def get_status() -> String:
    # You can call any real logic from your existing API here
    return "FungiForge MCP Host is online"

# 2. Create a schema with your functions
schema = Schema(
    name="FungiForge",
    description="Interact with the FungiForge mushroom monitoring system",
    functions=[get_status]
)

# 3. Create an MCP Host and register schema
mcp_host = Host(schemas=[schema])

# 4. Mount it to FastAPI
app = FastAPI()
app.mount("/.well-known/mcp", mcp_host.app)
