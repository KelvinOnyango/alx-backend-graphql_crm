from datetime import datetime
import requests

# Task 2 — Heartbeat Logger
def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    try:
        response = requests.post("http://localhost:8000/graphql", json={"query": "{ hello }"})
        hello = response.json().get("data", {}).get("hello", "No response")
    except Exception:
        hello = "GraphQL unavailable"
    with open("/tmp/crm_heartbeat_log.txt", "a") as log:
        log.write(f"{timestamp} CRM is alive - {hello}\n")


# ✅ Task 3 — Update Low Stock Products using gql
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


"""Task 3 — Update Low Stock Products
This task updates low stock products by executing a GraphQL mutation."""
def update_low_stock():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Set up gql transport
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Define mutation
    mutation = gql("""
    mutation {
        updateLowStockProducts {
            success
            updatedProducts
        }
    }
    """)

    try:
        result = client.execute(mutation)
        updates = result.get("updateLowStockProducts", {}).get("updatedProducts", [])

        with open("/tmp/low_stock_updates_log.txt", "a") as log:
            for product in updates:
                log.write(f"{timestamp} - {product}\n")
    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as log:
            log.write(f"{timestamp} - Error: {str(e)}\n")