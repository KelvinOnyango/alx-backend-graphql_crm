from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def update_low_stock():
    """Update low stock products every 12 hours"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
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
            f.write(f"\n[{timestamp}] Stock Update Report\n")
            f.write(f"Status: {result['updateLowStockProducts']['message']}\n")
            if result['updateLowStockProducts']['updatedProducts']:
                f.write("Updated Products:\n")
                for product in result['updateLowStockProducts']['updatedProducts']:
                    f.write(f"- {product}\n")
    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"\n[{timestamp}] ERROR: {str(e)}\n")