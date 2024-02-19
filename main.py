"""
main.py
FastAPI Tutorial
Usage: uvicorn main:app --reload
"""
from enum import Enum
from typing import Union

from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Required


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# create the data model
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


# create a FastAPI instance
app = FastAPI()


# create a path operation decorator
@app.get("/")
async def root():
    """
    define the path operation function
    """
    # return the content
    return {"message": "Hello World"}


## Path Parameters
# Path parameters with types
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


# Order matters
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


# Predefined values
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


# Declare a path parameter
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # Working with Python enumerations
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    # Get the enumeration value
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    # Return enumeration members
    return {"model_name": model_name, "message": "Have some residuals"}


# Path parameters containing paths
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


## Query Parameters
# When we declare function parameters that are not part of the path parameters,
# they are automatically interpreted as "query" parameters.
# http://127.0.0.1:8000/items/?skip=0&limit=10
# http://127.0.0.1:8000/items/
@app.get("/query/")
async def read_item_query(skip: int = 0, limit: int = 10):
    """
    skip is an int with a default value of 0
    limit is an int with a default value of 10
    """
    return fake_items_db[skip : skip + limit]


# Optional parameters
@app.get("/query/optional/{item_id}")
async def read_item_optional(item_id: str, q: Union[str, None] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# Query parameter type conversion
# http://127.0.0.1:8000/items/foo?short=false
@app.get("/query/{item_id}")
async def read_item_bool(item_id: str, q: Union[str, None] = None, short: bool = False):
    """
    item_id is a required string
    q is an optional string
    short is an bool with a default value of False
    """
    item = {"item_id": item_id}

    if q:
        item.update({"q": q})

    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Multiple path and query parameters
# We do not have to declare them in any specific order
# since they will be detected by name.
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Required query parameters
# When we want to make a query parameter required,
# we do not declare a default value.
# http://127.0.0.1:8000/query/items/3?needy=hello
@app.get("/query/items/{item_id}")
async def read_user_item_required(
    item_id: str, needy: str, skip: int = 0, limit: Union[int, None] = None
):
    """
    needy is a required query parameter of type str
    skip is an int with default value of 0
    limit is an optional int
    """
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


# Request Body
# To send data, we should use: POST (most common), PUT, DELETE, or PATCH.
@app.post("/request/items/")
async def create_item(item: Item):
    item_dict = item.dict()

    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    return item_dict


# Request body + path parameters
@app.put("/request/items/{item_id}")
async def create_item_body_path(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


# Request body + path + query parameters
@app.put("/request/items/{item_id}")
async def create_item_query(item_id: int, item: Item, q: Union[str, None] = None):
    result = {"item_id": item_id, **item.dict()}

    if q:
        result.update({"q": q})

    return result


# Query Parameters and String Validations

# Additional validation
# Use Query as the default value
@app.get("/params/items/")
async def read_items(q: Union[str, None] = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Add more validations
# Add regular expressions

# Default values
@app.get("/params/default/")
async def read_items(q: str = Query(default="fixedquery", min_length=3)):
    """
    q query parameter has min_length of 3 with default value of "fixedquery".
    Having a default value also makes the parameter optional.
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Make it required
# If need to declare a value as required when using Query,
# we can simply not declare a default value.
# http://127.0.0.1:8000/params/required/
# http://127.0.0.1:8000/params/required/?q=hello
@app.get("/params/required/")
async def read_items(q: str = Query(min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Required with None
@app.get("/params/none/")
async def read_items(q: Union[str, None] = Query(default=..., min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Use Pydantic Required instead of Ellipsis
# If you feel uncomfortable using ..., you can also import and use Required from Pydantic.
@app.get("/params/required/")
async def read_items(q: str = Query(default=Required, min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Query parameter list / multiple values
# http://localhost:8000/items/?q=foo&q=bar
@app.get("/params/multiple/")
async def read_items(q: Union[list[str], None] = Query(default=None)):
    """
    q can appear multiple times in the URL
    """
    query_items = {"q": q}
    return query_items


# Query parameter list / multiple values with defaults
# We can also define a default list of values if none are provided.
# FastAPI will not check the contents of the list.
@app.get("/params/multiple/defaults/")
async def read_items(q: list[str] = Query(default=["foo", "bar"])):
    query_items = {"q": q}
    return query_items


# Path Parameters and Numeric Validations
# We can declare the same type of validations and metadata for path parameters.
@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(title="The ID of the item to get"),
    q: Union[str, None] = Query(default=None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Order the parameters as you need
@app.get("/items/{item_id}")
async def read_items(q: str, item_id: int = Path(title="The ID of the item to get")):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Number validations: greater than and less than or equal
@app.get("/items/{item_id}")
async def read_items(
    *,
    item_id: int = Path(title="The ID of the item to get", gt=0, le=1000),
    q: str,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
