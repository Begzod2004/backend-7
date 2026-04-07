from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TelegramUser
from .serializers import TelegramUserSerializer, TelegramConnectSerializer


class TelegramConnectView(APIView):
    """Connect the authenticated user to a Telegram chat."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if user already connected
        if TelegramUser.objects.filter(user=request.user).exists():
            return Response(
                {'detail': 'Siz allaqachon Telegramga ulangansiz.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TelegramConnectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telegram_user = TelegramUser.objects.create(
            user=request.user,
            telegram_chat_id=serializer.validated_data['chat_id'],
        )

        return Response(
            TelegramUserSerializer(telegram_user).data,
            status=status.HTTP_201_CREATED,
        )


class TelegramStatusView(APIView):
    """Check if the authenticated user has a connected Telegram account."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            telegram_user = TelegramUser.objects.get(user=request.user)
            return Response({
                'connected': True,
                'telegram_chat_id': telegram_user.telegram_chat_id,
                'is_active': telegram_user.is_active,
                'connected_at': telegram_user.connected_at,
            })
        except TelegramUser.DoesNotExist:
            return Response({
                'connected': False,
            })


class TelegramDisconnectView(APIView):
    """Disconnect the authenticated user from Telegram."""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            telegram_user = TelegramUser.objects.get(user=request.user)
            telegram_user.delete()
            return Response(
                {'detail': 'Telegram muvaffaqiyatli uzildi.'},
                status=status.HTTP_204_NO_CONTENT,
            )
        except TelegramUser.DoesNotExist:
            return Response(
                {'detail': 'Telegram ulanmagan.'},
                status=status.HTTP_404_NOT_FOUND,
            )
