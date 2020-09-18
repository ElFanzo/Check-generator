from rest_framework.decorators import api_view

from .serializers import OrderSerializer
from .services import create_checks, get_check_pdf_file, get_rendered_checks


@api_view(["POST"])
def create_checks_view(request):
    """Create checks for an order."""
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return create_checks(request.data)


@api_view()
def get_new_checks(request):
    """Get a list of rendered checks."""
    return get_rendered_checks(request.GET.get("api_key"))


@api_view()
def get_check(request):
    """Get a PDF-file of the check to print it."""
    return get_check_pdf_file(request.GET.get("api_key"), request.GET.get("check_id"))
