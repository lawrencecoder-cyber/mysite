from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast(data):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "stocks",
        {
            "type": "send_stock_update",
            "data": data
        }
    )
