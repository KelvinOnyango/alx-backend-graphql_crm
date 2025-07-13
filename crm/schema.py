import graphene
from graphene_django import DjangoObjectType
from customers.models import Customer
from orders.models import Order
from products.models import Product

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello!")
    all_customers = graphene.List(CustomerType)
    pending_orders = graphene.List(OrderType, last_days=graphene.Int())
    
    def resolve_all_customers(self, info):
        return Customer.objects.all()
    
    def resolve_pending_orders(self, info, last_days=7):
        from django.utils import timezone
        from datetime import timedelta
        date_threshold = timezone.now() - timedelta(days=last_days)
        return Order.objects.filter(
            order_date__gte=date_threshold,
            status='pending'
        )

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(graphene.String)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []
        
        for product in low_stock_products:
            original_stock = product.stock
            product.stock += 10
            product.save()
            updated.append(f"{product.name} (Stock: {original_stock}→{product.stock})")
        
        return UpdateLowStockProducts(
            success=True,
            message=f"Updated {len(updated)} products",
            updated_products=updated
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)