#!/usr/bin/env python3
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure GraphQL client
transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# Query for recent pending orders
query = gql("""
query {
    pendingOrders(lastDays: 7) {
        id
        customer {
            email
        }
    }
}
""")

try:
    result = client.execute(query)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("/tmp/order_reminders_log.txt", "a") as f:
        for order in result['pendingOrders']:
            log_entry = f"[{timestamp}] Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n"
            f.write(log_entry)
    
    print("Order reminders processed!")
except Exception as e:
    print(f"Error processing order reminders: {str(e)}")