from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.models import CustomUser
from apps.users.serializers import UserSerializer


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')
        user = authenticate(username=phone, password=password)
        if not user:
            raise serializers.ValidationError('Telefon raqam yoki parol noto\'g\'ri')
        if not user.is_active:
            raise serializers.ValidationError('Foydalanuvchi bloklangan')
        data['user'] = user
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()
    new_password = serializers.CharField(min_length=6)

    def validate_phone(self, value):
        if not CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Bu telefon raqam topilmadi')
        return value
