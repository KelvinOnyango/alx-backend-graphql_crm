import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from graphene import relay
from django_filters import FilterSet, OrderingFilter
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)
        filterset_class = CustomerFilter

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)
        filterset_class = ProductFilter

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)
        filterset_class = OrderFilter

class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerNode)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(
                customer=customer, 
                message="Customer created successfully"
            )
        except Exception as e:
            raise Exception(str(e))

class BulkCreateCustomersInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(BulkCreateCustomersInput, required=True)

    customers = graphene.List(CustomerNode)
    errors = graphene.List(graphene.String)

    def mutate(self, info, inputs):
        customers = []
        errors = []
        
        for input in inputs:
            try:
                customer = Customer(
                    name=input.name,
                    email=input.email,
                    phone=input.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(f"Failed to create {input.name}: {str(e)}")
        
        return BulkCreateCustomers(
            customers=customers, 
            errors=errors
        )

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductNode)

    def mutate(self, info, input):
        try:
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock or 0
            )
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except Exception as e:
            raise Exception(str(e))

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderNode)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
            products = Product.objects.filter(pk__in=input.product_ids)
            
            if not products.exists():
                raise Exception("At least one product must be selected")
            
            order = Order(customer=customer)
            order.save()
            order.products.set(products)
            order.save()  # Re-save to calculate total_amount
            
            return CreateOrder(order=order)
        except Exception as e:
            raise Exception(str(e))

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    customer = relay.Node.Field(CustomerNode)
    all_customers = DjangoFilterConnectionField(CustomerNode)
    
    product = relay.Node.Field(ProductNode)
    all_products = DjangoFilterConnectionField(ProductNode)
    
    order = relay.Node.Field(OrderNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    def resolve_all_customers(self, info, **kwargs):
        return Customer.objects.all()

    def resolve_all_products(self, info, **kwargs):
        return Product.objects.all()

    def resolve_all_orders(self, info, **kwargs):
        return Order.objects.all()

schema = graphene.Schema(query=Query, mutation=Mutation)