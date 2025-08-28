from django.contrib.auth.models import Group, User
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from api.models import Owner, Dog, Health


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
    # owner = OwnerSerializer(read_only=True)
    # owner_data = serializers.DictField(write_only=True)
    # name = serializers.CharField(max_length=20)
    # age = serializers.IntegerField()
    # birth_date = serializers.DateTimeField()
    # gender = serializers.CharField(max_length=5)
    # size = serializers.CharField(max_length=10)
    # breed = serializers.CharField(max_length=100)
    # instagram = serializers.CharField(max_length=100)

    class Meta:
        model = Dog
        fields = '__all__'

