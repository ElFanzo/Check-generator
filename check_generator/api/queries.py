from .models import Check, Printer


def get_point_printers(point_id: str):
    return Printer.objects.filter(point_id=point_id).all()


def is_checks_exist(order_id: str):
    return Check.objects.filter(order__id=order_id).exists()


def save_checks_for_point(data, printers):
    """Save checks in DB for each point's Printer."""
    for printer in printers:
        yield printer.checks.create(type=printer.check_type, order=data, status="new")


def get_printer_by_api_key(api_key: str):
    return Printer.objects.get(api_key=api_key)


def get_rendered_checks_ids(checks):
    return checks.filter(status="rendered").values_list("id", flat=True)


def get_check(check_id: int):
    return Check.objects.get(pk=check_id)
