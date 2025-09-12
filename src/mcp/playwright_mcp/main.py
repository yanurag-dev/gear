from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

@app.get("/")
async def read_root():
    return {"message": "Playwright MCP is running!"}

@app.post("/items/")
async def create_item(item: Item):
    return item

# To run this application, navigate to the project root in your terminal and execute:
# uvicorn mcp.playwright_mcp.main:app --reload
