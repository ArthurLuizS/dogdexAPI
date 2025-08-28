from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response

from .models import  Dog, Owner, Health
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action

from api.serializers import GroupSerializer, UserSerializer, DogSerializer, OwnerSerializer, HealthSerializer


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




class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
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