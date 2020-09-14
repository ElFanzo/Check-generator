from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from rest_framework.views import Response

from .queries import *
from .tasks import async_generate_checks


def create_checks(data):
    """Create checks and run async workers to generate PDF files.

    :param data: request data
    :return:
    """
    point_printers = get_point_printers(data["point_id"])
    if not point_printers:
        return Response(
            {"error": "Для данной точки не настроено ни одного принтера"}, 400
        )

    if is_checks_exist(data["id"]):
        return Response({"error": "Для данного заказа уже созданы чеки"}, 400)

    checks = [check for check in save_checks_for_point(data, point_printers)]

    async_generate_checks.delay(checks)

    return Response({"ok": "Чеки успешно созданы"}, 200)


def get_rendered_checks(api_key: str):
    """Get rendered checks for a Printer with the given api_key."""
    try:
        printer = get_printer_by_api_key(api_key)
    except ObjectDoesNotExist:
        return Response({"error": "Ошибка авторизации"}, 401)
    return Response(
        {
            "checks": [
                {"id": check_id}
                for check_id in get_rendered_checks_ids(printer.checks)
            ]
        },
        200
    )


def get_check_pdf_file(api_key: str, check_id: int):
    try:
        get_printer_by_api_key(api_key)
    except ObjectDoesNotExist:
        return Response({"error": "Ошибка авторизации"}, 401)

    try:
        check = get_check(int(check_id))
    except ObjectDoesNotExist:
        return Response({"error": "Данного чека не существует"}, 400)

    if check.status == "new":
        return Response({"error": "Для данного чека не сгенерирован PDF-файл"}, 400)

    file_response = get_file_response(check.pdf_file.file)

    check.status = "printed"
    check.save()

    return file_response


def get_file_response(file):
    return FileResponse(file, content_type="application/pdf")
