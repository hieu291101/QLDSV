import re

from rest_framework import serializers, validators
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    def email_school(value):
        if not re.match(r'\b[A-Za-z0-9._%+-]+@ou\.edu\.vn', value):
            raise serializers.ValidationError('This field must be @ou.edu.vn')

    email = serializers.EmailField(
        required=True,
        validators=[
            validators.UniqueValidator(queryset=User.objects.all()),
            email_school
        ]
    )
    student_number = serializers.CharField(required=True, validators=[validators.UniqueValidator(User.objects.all())])
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'student_number', 'password', 'password2',
                  'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            student_number=validated_data['student_number'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['student_number', 'first_name', 'last_name', 'email']