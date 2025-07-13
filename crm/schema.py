import graphene
from graphene_django import DjangoObjectType
from products.models import Product

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

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

schema = graphene.Schema(mutation=Mutation)