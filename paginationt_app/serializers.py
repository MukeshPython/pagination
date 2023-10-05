from rest_framework import serializers
from .models import Pagination


class paginationserializer(serializers.ModelSerializer):
    class Meta:
        model = Pagination
        fields = '__all__'
