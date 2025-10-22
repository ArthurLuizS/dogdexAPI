from django.contrib.auth.models import Group, User
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from api.models import Owner, Dog, Health, ServiceRecord, ServiceType, Stay
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError
from django.db.models import Sum

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


# Serializer Para primeiro cadastro (payload completo do front: owner, dog e health)
class DogNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        exclude = ["owner"]  # setado no create

class HealthNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Health
        exclude = ["dog"]    # setado no create


class OwnerFullSerializer(serializers.ModelSerializer):
    dog = DogNestedSerializer(write_only=True)
    health = HealthNestedSerializer(write_only=True)

    class Meta:
        model = Owner
        fields = [
            "id", "name", "phone", "email", "cpf", "address", "district",
            "dog", "health"
        ]

    @transaction.atomic
    def create(self, validated_data):
        dog_data = validated_data.pop("dog")
        health_data = validated_data.pop("health")

        try:
            owner = Owner.objects.create(**validated_data)
        except IntegrityError as e:
            raise ValidationError({"cpf": "Já existe um tutor com este CPF."})

        dog = Dog.objects.create(owner=owner, **dog_data)
        Health.objects.create(dog=dog, **health_data)

        return owner

    def to_representation(self, instance):
        # devolve tudo já aninhado, bom pro front
        data = super().to_representation(instance)
        data["dog"] = DogNestedSerializer(instance.dogs.first()).data if instance.dogs.exists() else None
        dog = instance.dogs.first() if instance.dogs.exists() else None

        if dog:
            try:
                health = dog.health
            except Health.DoesNotExist:
                health = None
        else:
            health = None

        data["health"] = HealthNestedSerializer(health).data if health else None
        return data


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ["id", "name", "description", "base_price"]


class StaySerializer(serializers.ModelSerializer):
    dog_name = serializers.CharField(source="dog.name", read_only=True)
    owner = serializers.UUIDField(source="dog.owner.id", read_only=True) # snapshot implícito
    total_with_services = serializers.SerializerMethodField()
    class Meta:
        model = Stay
        fields = '__all__'

    def get_total_with_services(self, obj):
        # soma dos serviços relacionados + price_total da hospedagem
        services_total = obj.services.aggregate(total=Sum('price'))['total'] or 0
        return obj.price_total + services_total

    def create(self, validated_data):
        dog = validated_data.get("dog")
        validated_data["owner"] = dog.owner
        return super().create(validated_data)

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