import uuid
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.indexes import BTreeIndex


class Owner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Evita perder histórico se excluírem o tutor:
    owner = models.ForeignKey(Owner, on_delete=models.PROTECT, related_name="dogs")
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    size = models.CharField(max_length=10, choices=Size.choices)
    breed = models.CharField(max_length=100, default='SRD')
    instagram = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # opcional: soft-delete

    def __str__(self):
        return f"{self.name} ({self.owner.name})"


class Health(models.Model):
    dog = models.OneToOneField(Dog, on_delete=models.CASCADE, related_name="health")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    has_vet = models.BooleanField(default=False)
    vet_name = models.CharField(max_length=100, null=True, blank=True)
    vet_phone = models.CharField(max_length=20, null=True, blank=True)

    castrated = models.BooleanField(default=False)
    in_heat = models.BooleanField(default=False)

    chronic_disease = models.BooleanField(default=False)
    disease_description = models.TextField(null=True, blank=True)

    allergies = models.TextField(null=True, blank=True)
    special_recommendations = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Dados de saúde de {self.dog.name}"


class ServiceType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class Stay(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dog = models.ForeignKey(Dog, on_delete=models.PROTECT, related_name="stays")
    owner = models.ForeignKey(Owner, on_delete=models.PROTECT, related_name="stays")  # snapshot do tutor
    check_in = models.DateTimeField(null=True, blank=True)   # use DateField se preferir
    check_out = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        indexes = [
            BTreeIndex(fields=["dog", "check_in"]),
            BTreeIndex(fields=["check_in"]),
        ]
        ordering = ["-check_in"]

    def clean(self):
        if self.check_in and self.check_out and self.check_out < self.check_in:
            raise ValidationError("check_out não pode ser anterior ao check_in.")

    def __str__(self):
        return f"Hospedagem de {self.dog.name} ({self.check_in} → {self.check_out})"


class ServiceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dog = models.ForeignKey(Dog, on_delete=models.PROTECT, related_name="services")
    owner = models.ForeignKey(Owner, on_delete=models.PROTECT, related_name="services")  # snapshot do tutor
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)

    performed_at = models.DateTimeField(null=True, blank=True)  # eventos com hora (banho, transporte)
    day = models.DateField(null=True, blank=True)               # presença/diária (creche)

    stay = models.ForeignKey(Stay, on_delete=models.SET_NULL, null=True, blank=True, related_name="services")

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="BRL")

    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            BTreeIndex(fields=["dog", "performed_at"]),
            BTreeIndex(fields=["dog", "day"]),
            BTreeIndex(fields=["created_at"]),
        ]
        ordering = ["-performed_at", "-day", "-created_at"]

    def clean(self):
        if not self.performed_at and not self.day:
            raise ValidationError("Informe performed_at (pontual) ou day (diário).")
        if self.performed_at and self.day:
            raise ValidationError("Use apenas um: performed_at OU day.")
        if self.stay and self.stay.dog_id != self.dog_id:
            raise ValidationError("O ServiceRecord deve referenciar a mesma dog de Stay.")

    def save(self, *args, **kwargs):
        # Preenche snapshot do owner e preço padrão
        if not self.owner_id:
            self.owner = self.dog.owner
        if self.price is None and self.service_type and self.service_type.base_price is not None:
            self.price = self.service_type.base_price
        super().save(*args, **kwargs)

    def __str__(self):
        when = self.performed_at.date() if self.performed_at else self.day
        return f"{self.service_type.name} - {self.dog.name} ({when})"