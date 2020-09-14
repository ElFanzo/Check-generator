from rest_framework import serializers


class ItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.IntegerField()


class ClientSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone = serializers.CharField()


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    items = serializers.ListField(child=ItemSerializer())
    price = serializers.IntegerField()
    address = serializers.CharField()
    client = ClientSerializer()
    point_id = serializers.CharField()
