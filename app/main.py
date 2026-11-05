"""Tiny in-memory 'store' API used as the target for the load tests.

Self-contained on purpose: load testing must run against our own instance,
never against a third party's public service.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Demo Store API")

PRODUCTS = [{"id": i, "name": f"Produto {i}", "price": round(9.9 * i, 2)} for i in range(1, 21)]
ORDERS: dict[int, dict] = {}
_counter = {"n": 0}


class OrderIn(BaseModel):
    product_id: int
    quantity: int = 1


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def list_products():
    return PRODUCTS


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="product not found")


@app.post("/orders", status_code=201)
def create_order(order: OrderIn):
    if not any(p["id"] == order.product_id for p in PRODUCTS):
        raise HTTPException(status_code=404, detail="product not found")
    if order.quantity < 1:
        raise HTTPException(status_code=422, detail="quantity must be >= 1")
    _counter["n"] += 1
    order_id = _counter["n"]
    ORDERS[order_id] = {"id": order_id, **order.model_dump()}
    return ORDERS[order_id]
