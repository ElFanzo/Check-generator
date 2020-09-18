import json
import os

from django.conf import settings
from django.urls import reverse
from django_rq import get_worker
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Check, Printer


ORDER_DATA = """
{
  "id": 123456,
  "price": 780,
  "items": [
    {
      "name": "Вкусная пицца",
      "quantity": 2,
      "unit_price": 250
    },
    {
      "name": "Не менее вкусные роллы",
      "quantity": 1,
      "unit_price": 280
    }
  ],
  "address": "г. Уфа, ул. Ленина, д. 42",
  "client": {
    "name": "Иван",
    "phone": 9173332222
  },
  "point_id": 10201
}
"""


class CreateChecksViewTests(APITestCase):
    fixtures = ["printers.json"]

    def setUp(self):
        self.data = json.loads(ORDER_DATA)
        self.url = reverse("create_checks")

    def test_create_checks_for_point_with_printers(self):
        response = self.get_response()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["ok"], "Чеки успешно созданы")

        checks = Check.objects.filter(order__id=self.data["id"])
        self.assertEqual(checks.count(), 2)
        self.assertListEqual(list(checks.values_list("status", flat=True)), ["new", "new"])

        get_worker().work(burst=True)
        for check in checks:
            filename = f"{os.path.join(settings.PDF_URL, str(self.data['id']))}_{check.type}.pdf"
            self.assertEqual(check.status, "rendered")
            self.assertEqual(check.pdf_file.url[1:], filename)

    def test_create_checks_for_point_with_no_printer(self):
        self.data["point_id"] = "10209"
        response = self.get_response()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Для данной точки не настроено ни одного принтера")

    def test_create_checks_twice(self):
        self.get_response()
        get_worker().work(burst=True)
        response = self.get_response()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Для данного заказа уже созданы чеки")

    def test_create_checks_with_missing_order_data(self):
        self.data.pop("price")
        self.data.pop("point_id")
        response = self.get_response()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response.json()["price"], ["This field is required."])
        self.assertListEqual(response.json()["point_id"], ["This field is required."])

    def get_response(self):
        return self.client.post(self.url, self.data, format="json")

    def tearDown(self):
        delete_checks_pdf_files()


class GetNewChecksViewTests(APITestCase):
    fixtures = ["printers.json"]

    def setUp(self):
        self.data = json.loads(ORDER_DATA)
        self.printer_api_key = Printer.objects.get(point_id=self.data["point_id"], check_type="client").api_key
        self.url = reverse("new_checks")

    def test_get_one_check_id_for_printer_with_correct_api_key(self):
        self.create_checks()
        self.url = f"{self.url}?api_key={self.printer_api_key}"
        response = self.get_response()

        check = Printer.objects.get(api_key=self.printer_api_key).checks.first()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json()["checks"], [{"id": check.id}])

    def test_get_checks_ids_for_printer_with_incorrect_api_key(self):
        self.url = f"{self.url}?api_key=1111111"
        response = self.get_response()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Ошибка авторизации")

    def test_get_two_checks_ids_for_printer(self):
        self.create_checks()
        self.create_checks(123457)
        self.url = f"{self.url}?api_key={self.printer_api_key}"
        response = self.get_response()

        checks_ids = Printer.objects.get(api_key=self.printer_api_key).checks.values_list("id", flat=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json()["checks"], [{"id": id_} for id_ in checks_ids])

    def get_response(self):
        return self.client.get(self.url)

    def create_checks(self, order_id: int = 123456):
        self.data["id"] = order_id
        self.client.post(reverse("create_checks"), self.data, format="json")
        get_worker().work(burst=True)

    def tearDown(self):
        delete_checks_pdf_files()


class GetChekViewTests(APITestCase):
    fixtures = ["printers.json"]

    def setUp(self):
        self.data = json.loads(ORDER_DATA)
        self.printer = Printer.objects.get(point_id=self.data["point_id"], check_type="client")
        self.url = reverse("check")

    def test_get_checks_content(self):
        self.create_checks()
        check_id = self.printer.checks.first().id
        url = f"{self.url}?api_key={self.printer.api_key}&check_id={check_id}"
        response = self.get_response(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_get_not_existing_checks_content(self):
        self.create_checks()
        url = f"{self.url}?api_key={self.printer.api_key}&check_id=999"
        response = self.get_response(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Данного чека не существует")

    def test_get_new_checks_content(self):
        self.create_checks(run_worker=False)
        check_id = self.printer.checks.first().id
        url = f"{self.url}?api_key={self.printer.api_key}&check_id={check_id}"
        response = self.get_response(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Для данного чека не сгенерирован PDF-файл")

    def test_get_checks_content_with_incorrect_printers_api_key(self):
        self.create_checks()
        check_id = self.printer.checks.first().id
        url = f"{self.url}?api_key=999999&check_id={check_id}"
        response = self.get_response(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Ошибка авторизации")

    def get_response(self, url):
        return self.client.get(url)

    def create_checks(self, run_worker=True):
        self.client.post(reverse("create_checks"), self.data, format="json")
        if run_worker:
            get_worker().work(burst=True)

    def tearDown(self):
        delete_checks_pdf_files()


def delete_checks_pdf_files():
    for check in Check.objects.all():
        if check.pdf_file.name:
            os.remove(os.path.join(settings.MEDIA_URL[1:], check.pdf_file.name))
