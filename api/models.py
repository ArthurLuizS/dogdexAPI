from django.db import models

# Create your models here.

from django.db import models
import uuid


class Owner(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True)
    address = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Dog(models.Model):
    class Size(models.TextChoices):
        PEQUENO = "P", "Pequeno"
        MEDIO = "M", "Médio"
        GRANDE = "G", "Grande"

    class Gender(models.TextChoices):
        MACHO = "M", "Macho"
        FEMEA = "F", "Fêmea"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="dogs")
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    size = models.CharField(max_length=10, choices=Size.choices)
    breed = models.CharField(max_length=100, default='SRD')
    instagram = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.owner.name})"


class Health(models.Model):
    dog = models.OneToOneField(Dog, on_delete=models.CASCADE, related_name="health")
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    has_vet = models.BooleanField(default=False)
    vet_name = models.CharField(max_length=100,null=True, blank=True)
    vet_phone = models.CharField(max_length=20, null=True, blank=True)

    castrated = models.BooleanField(default=False)
    in_heat = models.BooleanField(default=False)

    chronic_disease = models.BooleanField(default=False)
    disease_description = models.TextField(null=True, blank=True)

    allergies = models.TextField(null=True, blank=True)
    special_recommendations = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Dados de saúde de {self.dog.name}"
