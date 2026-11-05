"""Load profile + SLA gate for the Demo Store API.

Models a shopper browsing the catalog and occasionally placing an order,
with task weights reflecting realistic traffic (more reads than writes).

The SLA is enforced in code (via the `quitting` event): the process exits
non-zero if the failure ratio or the p95 response time breach the budget,
so the CI goes red when performance regresses.
"""
import logging
import random

from locust import HttpUser, events, task, between

# --- Service Level Agreement (the performance budget) ---
SLA_MAX_FAIL_RATIO = 0.01   # at most 1% of requests may fail
SLA_MAX_P95_MS = 500        # 95th percentile must stay under 500 ms


class ShopperUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def browse_catalog(self):
        self.client.get("/products")

    @task(3)
    def view_product(self):
        product_id = random.randint(1, 20)
        self.client.get(f"/products/{product_id}", name="/products/[id]")

    @task(2)
    def place_order(self):
        payload = {"product_id": random.randint(1, 20), "quantity": random.randint(1, 3)}
        self.client.post("/orders", json=payload)

    @task(1)
    def health_check(self):
        self.client.get("/health")


@events.quitting.add_listener
def enforce_sla(environment, **_kwargs):
    stats = environment.stats.total
    fail_ratio = stats.fail_ratio
    p95 = stats.get_response_time_percentile(0.95)

    environment.process_exit_code = 0
    if fail_ratio > SLA_MAX_FAIL_RATIO:
        logging.error("SLA FAIL: fail ratio %.2f%% > %.2f%%", fail_ratio * 100, SLA_MAX_FAIL_RATIO * 100)
        environment.process_exit_code = 1
    if p95 > SLA_MAX_P95_MS:
        logging.error("SLA FAIL: p95 %d ms > %d ms", p95, SLA_MAX_P95_MS)
        environment.process_exit_code = 1
    if environment.process_exit_code == 0:
        logging.info("SLA OK: fail ratio %.2f%%, p95 %d ms", fail_ratio * 100, p95)
