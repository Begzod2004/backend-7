from rest_framework import serializers
from .models import TelegramUser


class TelegramUserSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = TelegramUser
        fields = [
            'id', 'user', 'user_name', 'telegram_chat_id',
            'is_active', 'connected_at',
        ]
        read_only_fields = ['id', 'user', 'connected_at']

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None


class TelegramConnectSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()

    def validate_chat_id(self, value):
        if TelegramUser.objects.filter(telegram_chat_id=value).exists():
            raise serializers.ValidationError(
                "Bu Telegram Chat ID allaqachon boshqa foydalanuvchiga ulangan."
            )
        return value
