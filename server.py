from typing import Dict, Optional
from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


app = FastAPI(
    title="Items API",
    description=(
        "A simple API written to showcase FastAPI."
        "View routes, models, and responses below."
    ),
    version="1.0",
    contact={
        "name": "meizuflux",
        "url": "https://meizuflux.com",

    },
    license_info={
        "name": "The Unlicense",
        "url": "https://unlicense.org/"
    }
)

items = {}

class Item(BaseModel):
    name: str
    description: str
    price: float
    tags: list[str]

class PartialItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tags: Optional[list[str]] = None

class Message(BaseModel):
    message: str

@app.get("/", include_in_schema=False)
async def index():
    return HTMLResponse("This is a FastAPI demonstration. View docs at <a href='/docs'>/docs</a>")

@app.get(
    "/items",
    tags=["Items"],
    summary="Fetch all items",
    response_model=Dict[str, Item]
)
async def get_items():
    """
    Get a list of all items.
    """
    return items

@app.get(
    "/items/{item_id}",
    tags=["Items"],
    summary="Fetch an item",
    responses={
        200: {
            "model": Item,
            "description": "Item requested by id",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Soda",
                        "description": "A tasty, sugary drink.",
                        "price": 0.99,
                        "tags": ["drink", "tasty", "thirst-quencher"]
                    }
                }
            },
        },
    },
)
async def get_item(item_id: str):
    """
    Get an item by name.
    """
    return items.get(item_id)

@app.post(
    "/items/{item_id}",
    tags=["Items"],
    summary="Create an item",
    status_code=201,
    responses={
        409: {
            "model": Message,
            "description": "Specified item already exists",
            "content": {
                "application/json": {
                    "example": {"message": "Item with id 'soda' already exists."}
                }
            }
        },
        201: {
            "model": Item,
            "description": "Item was created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Soda",
                        "description": "A tasty, sugary drink.",
                        "price": 0.99,
                        "tags": ["drink", "tasty", "thirst-quencher"]
                    }
                }
            },
        },
    }
)
async def create_item(item_id, item: Item, request: Request, response: Response):
    """
    Create an item with all the information:

    - **name**: The name of the item
    - **description**: A description describing the item
    - **price**: The price of the item
    - **tags**: A set of tags that identify this item

    The path parameter **item_id** will be the identifier for this item.
    It should follow the snake_case naming convention.

    'Fizzy Drink' should become 'fizzy_drink'
    """
    if items.get(item_id) is not None:
        return JSONResponse({"message": f"Item with id '{item_id}' already exists."}, status_code=409)

    items[item_id] = jsonable_encoder(item)
    response.headers["Location"] = f'{str(request.base_url)}items/{item_id}'

    return item

@app.delete("/items/{item_id}", tags=["Items"], summary="Delete an item", status_code=204, responses={404: {"model": Message, "description": "No item was found to delete.", "content": {"application/json": {"example": {"message": "No item with id 'soda' found to delete."}}}}, 204: {
            "description": "Item deleted successfully",
        }})
async def delete_item(item_id: str):
    """
    Delete an item by id
    """
    item = items.pop(item_id, None)

    if item is None:
        return JSONResponse({"message": f"No item with id '{item_id}' found to delete."}, status_code=404)

    return Response()


@app.put(
    "/items/{item_id}",
    tags=["Items"],
    summary="Update an item",
    status_code=204,
    responses={
        404: {
            "model": Message,
            "description": "No item was found to update.",
            "content": {
                "application/json": {
                    "example": {"message": "Item with id 'soda' does not exist."}
                }
            },
        },
        204: {
            "description": "Item updated successfully",
        }
    }
)
async def update_item(item_id: str, item: Item):
    """
    Update an item by id

    You cannot create items via this endpoint, only update them
    """
    item = items.get(item_id)

    if item is None:
        return JSONResponse({"message": f"Item with id '{item_id}' does not exist."}, status_code=404)

    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return Response()

@app.patch(
    "/items/{item_id}",
    tags=["Items"],
    summary="Edit an item",
    status_code=204,
    responses={
        404: {
            "model": Message,
            "description": "No item was found to edit.",
            "content": {
                "application/json": {
                    "example": {"message": "Item with id 'soda' does not exist."}
                }
            },
        },
        204: {
            "description": "Item edited successfully",
        }
    }
)
async def edit_item(item_id: str, partial_item: PartialItem):
    item = items.get(item_id)

    if item is None:
        return JSONResponse({"message": f"Item with id '{item_id}' does not exist."}, status_code=404)

    item_model = Item(**item)
    update_data = partial_item.dict(exclude_unset=True)
    updated_item = item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)

    return Response()