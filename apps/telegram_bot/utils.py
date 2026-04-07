import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message):
    """Send message to telegram user. Non-blocking, errors are logged not raised."""
    try:
        import httpx
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            return
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        httpx.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"Telegram xabar yuborishda xato: {e}")


def notify_stock_alert(batch):
    """Send stock alert to relevant users via Telegram."""
    from apps.telegram_bot.models import TelegramUser

    if batch.status == 'LOW':
        msg = (
            f"\u26a0\ufe0f <b>KAM ZAXIRA</b>\n"
            f"Mahsulot: {batch.product.name}\n"
            f"Ombor: {batch.warehouse.name}\n"
            f"Qolgan: {batch.quantity} {batch.unit.abbreviation}\n"
            f"Minimal: {batch.min_quantity}\n"
            f"Partiya: {batch.batch_number}"
        )
    elif batch.status == 'EMPTY':
        msg = (
            f"\U0001f6a8 <b>ZAXIRA TUGADI</b>\n"
            f"Mahsulot: {batch.product.name}\n"
            f"Ombor: {batch.warehouse.name}\n"
            f"Darhol buyurtma bering!"
        )
    else:
        return

    for tu in TelegramUser.objects.filter(is_active=True).select_related('user'):
        if tu.user.role in ('ADMIN', 'KATTA_OMBOR_ADMINI'):
            send_telegram_message(tu.telegram_chat_id, msg)


def notify_new_transfer(transfer):
    """Notify warehouse admin about new transfer."""
    from apps.telegram_bot.models import TelegramUser

    items_count = transfer.items.count()
    msg = (
        f"\U0001f4e6 <b>YANGI TRANSFER</b>\n"
        f"{transfer.transfer_number}\n"
        f"Kimdan: {transfer.from_warehouse.name}\n"
        f"Kimga: {transfer.to_warehouse.name}\n"
        f"Materiallar: {items_count} xil\n"
        f"Qabul qiling!"
    )

    # Notify to_warehouse responsible users
    for tu in TelegramUser.objects.filter(
        is_active=True, user__warehouse=transfer.to_warehouse
    ).select_related('user'):
        send_telegram_message(tu.telegram_chat_id, msg)


def notify_new_order(order):
    """Notify admins about new order."""
    from apps.telegram_bot.models import TelegramUser

    msg = (
        f"\U0001f4cb <b>YANGI BUYURTMA</b>\n"
        f"{order.order_number}\n"
        f"Ombor: {order.warehouse.name}\n"
        f"Jami: {order.total_amount:,.0f} so'm"
    )

    for tu in TelegramUser.objects.filter(is_active=True).select_related('user'):
        if tu.user.role in ('ADMIN', 'KATTA_OMBOR_ADMINI'):
            send_telegram_message(tu.telegram_chat_id, msg)
