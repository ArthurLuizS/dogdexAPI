from django.contrib.auth.models import Group, User
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from api.models import Owner, Dog, Health, ServiceRecord, ServiceType, Stay


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = '__all__'


class HealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Health
        fields = '__all__'


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = '__all__'


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ["id", "name", "description", "base_price"]


class StaySerializer(serializers.ModelSerializer):
    dog_name = serializers.CharField(source="dog.name", read_only=True)
    owner = serializers.UUIDField(source="dog.owner.id", read_only=True) # snapshot implícito
    class Meta:
        model = Stay
        fields = '__all__'

    def validate(self, attrs):
        check_in = attrs.get("check_in") or getattr(self.instance, "check_in", None)
        check_out = attrs.get("check_out") or getattr(self.instance, "check_out", None)
        if check_in and check_out and check_out < check_in:
            raise serializers.ValidationError("check_out não pode ser anterior ao check_in.")
        return attrs


class ServiceRecordSerializer(serializers.ModelSerializer):
    service_type_name = serializers.CharField(source="service_type.name", read_only=True)

    dog_name = serializers.CharField(source="dog.name", read_only=True)
    owner_name = serializers.CharField(source="owner.name", read_only=True)

    class Meta:
        model = ServiceRecord

    fields = [
        "id", "dog", "dog_name", "owner", "owner_name",
        "service_type", "service_type_name",
        "performed_at", "day", "stay",
        "price", "currency", "metadata", "notes", "created_at"
    ]
    read_only_fields = ["created_at"]

    def validate(self, attrs):
        performed_at = attrs.get("performed_at")

        day = attrs.get("day")
        if not performed_at and not day:
            raise serializers.ValidationError("Informe performed_at (pontual) ou day (diário).")
        if performed_at and day:
            raise serializers.ValidationError("Use apenas um: performed_at OU day.")
        return attrs