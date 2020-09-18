import codecs
import json

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.response import SimpleTemplateResponse
from django_rq import job


@job
def async_generate_checks(checks):
    """Asynchronously generate PDF files for each check."""
    for check in checks:
        content = make_pdf_from_html(check.type, check.order)
        check.status = "rendered"
        check.pdf_file.save(f"{check.order['id']}_{check.type}.pdf", ContentFile(content))


def make_pdf_from_html(check_type, order):
    """Get a PDF content from an HTML template with the given order data."""
    data = {
        'contents': codecs.encode(get_rendered_html(check_type, order), "base64").decode("utf-8"),
    }
    headers = {
        'Content-Type': 'application/json',
    }
    return requests.post(settings.WKHTMLTOPDF_URL, data=json.dumps(data), headers=headers).content


def get_rendered_html(check_type, order):
    template = SimpleTemplateResponse(f"api/{check_type}_check.html", {"order": order})
    template.render()
    return template.content
