import re

from rest_framework import serializers, validators
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from .models import *


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
        fields = ['student_number', 'email', 'first_name', 'last_name']

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Myclass
        fields = '__all__'

class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ['grade', 'gpa', 'rank', 'is_clock', 'course', 'mark_type']

class SaveMarkSerializer(serializers.ModelSerializer):
    grade = serializers.FloatField(max_value=10, min_value=0)

    class Meta:
        model = Mark
        fields = ['grade', 'course', 'is_clock', 'student', 'mark_type']

    def validate(self, attrs):
        if attrs['is_clock']:
            raise serializers.ValidationError(
                {"is_clock": "Can not save mark."})
        return attrs

    def create(self, validated_data):
        mark = Mark.objects.create(
            grade=validated_data['grade'],
            course=validated_data['course'],
            student=validated_data['student'],
            mark_type=validated_data['mark_type'],
            is_clock=validated_data['is_clock']
        )
        mark.save()
        return mark

class MarkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkType
        fields = ('type')

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class CourseRetrieveSerializer(serializers.Serializer):
    class Meta:
        model = Mark
        fields = ('course')

class CourseSerializer(serializers.Serializer):
    class Meta:
        model = Course
        fields = '__all__'

class ForumSerializer(serializers.Serializer):
    class Meta:
        model = Forum
        fields = '__all__'

class CommentSerializer(serializers.Serializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'sender', 'receiver', 'message', 'timestamp')
        read_only_fields = ('id', 'timestamp', 'firebase_key')

# class Save