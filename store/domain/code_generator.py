from datetime import datetime
from django.db import transaction
from store.models.sequence import Sequence

def generate_code(prefix):
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')

    with transaction.atomic():
        sequence, created = Sequence.objects.select_for_update().get_or_create(
            prefix=prefix,
            year=year,
            month=month
        )
        sequence.last_value += 1
        sequence.save()
        return f"{prefix}{year}{month}{sequence.last_value:04d}"
