from datetime import datetime


def generate_number(prefix, model_class, field_name):
    """Auto-generate numbers like BATCH-2025-0001, INV-2025-0001, ORD-2025-0001."""
    year = datetime.now().year
    prefix_str = f"{prefix}-{year}-"
    last_obj = model_class.objects.filter(
        **{f"{field_name}__startswith": prefix_str}
    ).order_by(f"-{field_name}").first()

    if last_obj:
        last_number = int(getattr(last_obj, field_name).split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix_str}{new_number:04d}"
