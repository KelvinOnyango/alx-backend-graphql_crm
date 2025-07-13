from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Log CRM system heartbeat every 5 minutes"""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("{ hello }")
        result = client.execute(query)
        status = "CRM and GraphQL are alive"
    except Exception as e:
        status = f"CRM is alive (GraphQL check failed: {str(e)})"
    
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(f"{timestamp} {status}\n")

def update_low_stock():
    """Update low stock products every 12 hours"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            headers={"Content-Type": "application/json"}
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        mutation = gql("""
        mutation {
            updateLowStockProducts {
                success
                message
                updatedProducts
            }
        }
        """)
        
        result = client.execute(mutation)
        
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            if result['updateLowStockProducts']['success']:
                f.write(f"[{timestamp}] {result['updateLowStockProducts']['message']}\n")
                for product in result['updateLowStockProducts']['updatedProducts']:
                    f.write(f"  - {product}\n")
            else:
                f.write(f"[{timestamp}] Stock update failed\n")
    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"[{timestamp}] Error updating stock: {str(e)}\n")