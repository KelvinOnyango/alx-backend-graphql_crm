#!/bin/bash

# Get script directory and project root using cwd concept
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cwd=$(pwd) && echo $cwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && cwd=$(pwd) && echo $cwd )"

# Change to project directory
cd "$PROJECT_ROOT" || exit 1

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
if [ -z "$DELETED_COUNT" ]; then
    echo "[$TIMESTAMP] Error: Could not determine deleted customer count" >> /tmp/customer_cleanup_log.txt
else
    echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
fi