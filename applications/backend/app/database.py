import os
from typing import List, Dict, Any

try:
    from azure.cosmos import CosmosClient
except Exception:
    CosmosClient = None

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "cloudmart"

_use_cosmos = (
    COSMOS_ENDPOINT
    and COSMOS_KEY
    and CosmosClient is not None
    and COSMOS_ENDPOINT.strip() != ""
    and COSMOS_KEY.strip() != ""
)

_fake_products = [
    {
        "id": "1",
        "name": "Wireless Headphones Pro",
        "description": "Premium noise-cancelling wireless headphones with 30hr battery",
        "category": "Electronics",
        "price": 199.99,
        "stock": 50
    },
    {
        "id": "2",
        "name": "4K Smart TV 55\"",
        "description": "55-inch Ultra HD Smart TV with HDR",
        "category": "Electronics",
        "price": 699.99,
        "stock": 20
    },
    {
        "id": "3",
        "name": "Office Chair Ergonomic",
        "description": "Adjustable armrests with lumbar support",
        "category": "Furniture",
        "price": 129.99,
        "stock": 15
    }
]

_fake_cart: List[Dict[str, Any]] = []
_fake_orders: List[Dict[str, Any]] = []

products_container = None
cart_container = None
orders_container = None

if _use_cosmos:
    try:
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        db = client.get_database_client(DATABASE_NAME)

        products_container = db.get_container_client("products")
        cart_container = db.get_container_client("cart")
        orders_container = db.get_container_client("orders")

        print("Using Cosmos DB")
    except Exception as e:
        print("Cosmos init failed → using local data")
        print(e)
        _use_cosmos = False
else:
    print("Cosmos not configured → using local data")


def get_products():
    if _use_cosmos:
        return list(products_container.read_all_items())
    return _fake_products


def get_product(product_id: str):
    if _use_cosmos:
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": product_id}]
        items = list(products_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        return items[0] if items else None

    for p in _fake_products:
        if p["id"] == product_id:
            return p
    return None


def get_categories():
    products = get_products()
    return sorted({p["category"] for p in products})


def get_cart():
    if _use_cosmos:
        return list(cart_container.read_all_items())
    return _fake_cart


def add_to_cart(item: dict):
    if _use_cosmos:
        cart_container.create_item(item)
    else:
        _fake_cart.append(item)
    return {"status": "added"}


def remove_from_cart(item_id: str):
    if _use_cosmos:
        cart_container.delete_item(item=item_id, partition_key=item_id)
    else:
        global _fake_cart
        _fake_cart = [i for i in _fake_cart if i.get("id") != item_id]
    return {"status": "removed"}


def create_order(order: dict):
    if _use_cosmos:
        orders_container.create_item(order)
    else:
        _fake_orders.append(order)
    return {"status": "order_created"}


def list_orders():
    if _use_cosmos:
        return list(orders_container.read_all_items())
    return _fake_orders
