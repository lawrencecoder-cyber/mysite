import json
from channels.generic.websocket import AsyncWebsocketConsumer

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "stocks_group"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # 🔥 This matches "type": "send_stock_update" from Celery
    async def send_stock_update(self, event):
        data = event["data"]

        await self.send(text_data=json.dumps({
            "type": "stock_update",
            "data": data
        }))
