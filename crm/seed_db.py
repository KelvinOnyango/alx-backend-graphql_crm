import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_data():
    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()

    # Create customers
    customers = [
        Customer(name="Alice", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol", email="carol@example.com"),
    ]
    Customer.objects.bulk_create(customers)

    # Create products
    products = [
        Product(name="Laptop", price=999.99, stock=10),
        Product(name="Mouse", price=19.99, stock=50),
        Product(name="Keyboard", price=49.99, stock=30),
    ]
    Product.objects.bulk_create(products)

    # Create orders
    alice = Customer.objects.get(email="alice@example.com")
    laptop = Product.objects.get(name="Laptop")
    mouse = Product.objects.get(name="Mouse")

    order = Order(customer=alice)
    order.save()
    order.products.add(laptop, mouse)
    order.save()

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()