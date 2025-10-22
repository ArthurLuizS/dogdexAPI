from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response

from .models import Dog, Owner, Health, ServiceType, Stay, ServiceRecord
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets, status, generics
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.serializers import (GroupSerializer, UserSerializer, DogSerializer, OwnerSerializer, HealthSerializer,StaySerializer, ServiceTypeSerializer, ServiceRecordSerializer, OwnerFullSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class OwnerFullCreateView(generics.CreateAPIView):
    """
    Endpoint para cadastrar Tutor + Dog + Health de uma vez.
    """
    queryset = Owner.objects.all()
    serializer_class = OwnerFullSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        owner = serializer.save()  # cria Owner, Dog e Health
        return Response(
            OwnerFullSerializer(owner).data,
            status=status.HTTP_201_CREATED
        )


class DogViewSet(viewsets.ModelViewSet):
    queryset = Dog.objects.all()
    serializer_class = DogSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            dog = Dog.objects.get(pk=kwargs['pk'])
            dog_serialized = DogSerializer(dog).data
        except Dog.DoesNotExist:
            return  Response({"error": "Dog not found"} ,status=404)

        try:
            owner = Owner.objects.get(pk=dog.owner_id)
        except Owner.DoesNotExist:
            return  Response({"error": "Owner not found"} ,status=404)

        dog_serialized.pop("owner", None)
        return Response({
            "dog": dog_serialized,
            "owner": OwnerSerializer(owner).data,
        })

    # timeline_schema = openapi.Response(
    #     description="Timeline",
    #     schema=openapi.Schema(
    #         type=openapi.TYPE_ARRAY,
    #         items=openapi.Items(
    #             type=openapi.TYPE_OBJECT,
    #             properties={
    #                 "id": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
    #                 "event_kind": openapi.Schema(type=openapi.TYPE_STRING),
    #                 "timestamp": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
    #             },
    #         ),
    #     ),
    # )
    # @swagger_auto_schema(responses={200: timeline_schema})
    @action(detail=True, methods=["get"], url_path="timeline")
    def timeline(self, request, pk=None):
        """Retorna a timeline unificada do cão (stays + services)."""
        dog = self.get_object()
        stays = list(Stay.objects.filter(dog=dog).values("id", "check_in", "check_out", "price_total", "notes"))
        for s in stays:
            s.update({
                "event_kind": "STAY",
                "timestamp": s["check_in"],
            })
        services = list(ServiceRecord.objects.filter(dog=dog).values("id", "service_type__name", "performed_at", "day",
                                                                 "price", "currency", "metadata", "notes", "created_at"))
        for e in services:
            e.update({
                "event_kind": "SERVICE",
                "service_type_name": e.pop("service_type__name"),
                "timestamp": e["performed_at"] or e["day"],
            })
        merged = stays + services
        merged.sort(key=lambda x: (x["timestamp"] or x.get("created_at")), reverse=True)
        return Response(merged)



class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all().order_by("name")
    serializer_class = OwnerSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            owner = self.get_object()
        except Owner.DoesNotExist:
            return Response({"error": "Owner not found"}, status=404)

        dogs = Dog.objects.filter(owner=owner)

        return Response({
            "owner": OwnerSerializer(owner).data,
            "dogs": list(dogs.values())
        })
    # @action(methods=['GET'],detail=True, url_path='dogs')
    # def search_owner_detail(self, request, *args, **kwargs):
    #     try:
    #         owner = self.get_object()
    #     except Owner.DoesNotExist:
    #         return Response({"error": "Owner not found"}, status=404)
    #     dogs = list(Dog.objects.filter(owner__id=kwargs['uuid_owner']).values())
    #     return Response({
    #         "dogs": dogs
    #     })


class HealthViewSet(viewsets.ModelViewSet):
    queryset = Health.objects.all()
    serializer_class = HealthSerializer


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all().order_by("name")
    serializer_class = ServiceTypeSerializer


class StayViewSet(viewsets.ModelViewSet):
    queryset = Stay.objects.all().select_related("dog", "dog__owner").all()
    serializer_class = StaySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["dog", "owner"]
    ordering_fields = ["check_in", "check_out"]


class ServiceRecordViewSet(viewsets.ModelViewSet):
    queryset = ServiceRecord.objects.select_related("dog", "owner", "service_type").all()
    serializer_class = ServiceRecordSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["dog", "owner", "service_type", "day"]
    search_fields = ["dog__name", "owner__name", "notes"]
    ordering_fields = ["performed_at", "day", "created_at", "price"]