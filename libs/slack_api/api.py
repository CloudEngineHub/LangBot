import json
from quart import Quart, jsonify,request
from slack_sdk.web.async_client import AsyncWebClient
from .slackevent import SlackEvent
from typing import Callable, Dict, Any
from pkg.platform.types import events as platform_events, message as platform_message

class SlackClient():
    
      def __init__(self,bot_token:str,signing_secret:str):

            self.bot_token = bot_token
            self.signing_secret = signing_secret
            self.app = Quart(__name__)
            self.client = AsyncWebClient(self.bot_token)
            self.app.add_url_rule('/callback/command', 'handle_callback', self.handle_callback_request, methods=['GET', 'POST'])
            self._message_handlers = {
            "example":[],
            }
            self.bot_user_id = None # avoid block

      async def handle_callback_request(self):
            try:
                  body = await request.get_data()
                  data = json.loads(body)
                  print("shoudao:")
                  print(data)
                  bot_user_id = data.get("event",{}).get("bot_id","")

                  if self.bot_user_id and bot_user_id == self.bot_user_id:
                        return jsonify({'status': 'ok'})
                  
                  if data and data.get("event", {}).get("channel_type") in ["im", "channel"]:
                        event = SlackEvent.from_payload(data)
                        await self._handle_message(event)
                        return jsonify({'status': 'ok'})
            
            except Exception as e:
                 raise(e)
            


      async def _handle_message(self, event: SlackEvent):
        """
        处理消息事件。
        """
        msg_type = event.type
        if msg_type in self._message_handlers:
            for handler in self._message_handlers[msg_type]:
                await handler(event)

      def on_message(self, msg_type: str):
        """注册消息类型处理器"""
        def decorator(func: Callable[[platform_events.Event], None]):
            if msg_type not in self._message_handlers:
                self._message_handlers[msg_type] = []
            self._message_handlers[msg_type].append(func)
            return func
        return decorator

      async def send_message_to_channle(self,text:str,channel_id:str):
            try:
                  response = await self.client.chat_postMessage(
                        channel=channel_id,
                        text=text
                  )
                  if self.bot_user_id is None and response.get("ok"):
                        self.bot_user_id = response["message"]["bot_id"]
                        print("bot_id:")
                        print(self.bot_user_id)
                  print("fanhui:")
                  print(response)
                  return 
            except Exception as e:
                  raise e

      async def send_message_to_one(self,text:str,user_id:str):
            try:
                  response = await self.client.chat_postMessage(
                        channel = '@'+user_id,
                        text= text
                  )
                  if self.bot_user_id is None and response.get("ok"):
                        self.bot_user_id = response["message"]["bot_id"]
                        print("bot_id:")
                        print(self.bot_user_id)
                  
                  return 
            except Exception as e:
                  raise e

      async def run_task(self, host: str, port: int, *args, **kwargs):
            """
            启动 Quart 应用。
            """
            await self.app.run_task(host=host, port=port, *args, **kwargs)





            


