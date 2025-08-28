from django.shortcuts import render
from django.http import HttpResponse
from .models import  Dog, Owner, Health
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

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


class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer


class HealthViewSet(viewsets.ModelViewSet):
    queryset = Health.objects.all()
    serializer_class = HealthSerializer