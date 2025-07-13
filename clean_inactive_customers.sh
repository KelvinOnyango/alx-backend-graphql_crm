#!/bin/bash

# Execute Django command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from orders.models import Order

year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(
    orders__isnull=True,
    last_order_date__lt=year_ago
).distinct()
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log results
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt