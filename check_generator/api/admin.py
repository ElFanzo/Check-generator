from django.contrib import admin

from .models import Check, Printer


class CheckAdmin(admin.ModelAdmin):
    list_filter = ["printer", "type", "status"]


admin.site.register(Check, CheckAdmin)
admin.site.register(Printer)
