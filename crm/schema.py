import graphene
from graphene_django import DjangoObjectType
from django.db.models import Sum
from products.models import Product
from customers.models import Customer
from orders.models import Order

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class Query(graphene.ObjectType):
    # CRM Report Queries
    total_customers = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()
    
    def resolve_total_customers(self, info):
        return Customer.objects.count()
    
    def resolve_total_orders(self, info):
        return Order.objects.count()
    
    def resolve_total_revenue(self, info):
        result = Order.objects.aggregate(total=Sum('total_amount'))
        return result['total'] or 0.0

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
            updated.append(f"{product.name} - Stock updated from {original_stock} to {product.stock}")
        
        return UpdateLowStockProducts(
            success=True if updated else False,
            message=f"Updated {len(updated)} product(s)" if updated else "No products needed restocking",
            updated_products=updated
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)