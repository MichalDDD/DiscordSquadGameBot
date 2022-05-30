from discord.ext import tasks
from a2s import SourceInfo
from a2s import info
from discord import Message
from discord.ext.commands import Bot
from discord import Intents
from discord import TextChannel
from discord.errors import NotFound
from modules.view_factory import MessageView
from modules.serverEmbed import ServerEmbed
from modules.view_factory import ServerButtonView

from modules.config_utils import get_config
from modules.config_utils import overwrite_config

layers_config_path = "./modules/layers.json"

layers = get_config(layers_config_path)

config_path = "./modules/config.json"

class DiscordClient(Bot):
    
    def __init__(self):
        self.config: dict = get_config(config_path)
        self.server_addresses: list[tuple] = []
        self.servers_queried: list[str] = []
        for key, value in self.config["servers_queried"].items():
            self.server_addresses.append((value["ip"], value["port"]))
            self.servers_queried.append(key)
        self.selected_server: int = 0
        self.channel: TextChannel = None
        self.message_layer: Message = None
        self.message_app_blufor: Message = None
        self.message_app_opfor: Message = None
        self.current_layer: str = None
        intents = Intents.default()
        intents.message_content = True
        self.server_button_view_done: bool = False
        super().__init__(command_prefix="/mydude", intents=intents)
    
    async def on_ready(self):
        self.channel = super().get_channel(self.config["discord_channel_id"])
        self.message_layer = await self.make_sure_message_present("message_layer_id")
        self.message_app_blufor = await self.make_sure_message_present("message_app_id_blufor")
        self.message_app_opfor = await self.make_sure_message_present("message_app_id_opfor")

        print(f"{super().user} is ready to fuck")
        self.send_server_info.start()

    async def make_sure_message_present(self, key: str) -> Message:
        msg: Message
        try:
            msg = await self.channel.fetch_message(self.config[key])
        except (NotFound, KeyError) as e:
            msg = await self.create_message(key)
        return msg

    async def create_message(self, key:str) -> Message:
        msg: Message = await self.channel.send("Starting up....")
        self.config[key] = msg.id
        overwrite_config(config_path, self.config)
        return msg
        
    @tasks.loop(seconds=5)
    async def send_server_info(self):
        source_info: list[SourceInfo] = []
        for address in self.server_addresses:
            source_info.append(info(address))
        if self.server_button_view_done:
            promise_layer =  self.message_layer.edit(content="", embed=ServerEmbed(source_info))
        else:
            server_button_labels: list[str] = [self.config["servers_queried"][self.servers_queried[0]]["tag"], self.config["servers_queried"][self.servers_queried[1]]["tag"], self.config["servers_queried"][self.servers_queried[2]]["tag"]]
            promise_layer = self.message_layer.edit(content="", embed=ServerEmbed(source_info), view=ServerButtonView(server_button_labels, self))
            self.server_button_view_done = True
        
        if source_info[self.selected_server].map_name != "Unknown":
            if source_info[self.selected_server].map_name != self.current_layer:
                self.current_layer = source_info[self.selected_server].map_name
                app_view_blufor = MessageView(self.current_layer, "BLUEFOR")
                promise_blufor = self.message_app_blufor.edit(content=f"{self.current_layer} TEAM 1", view=app_view_blufor, embed=app_view_blufor.embed)
                app_view_opfor = MessageView(self.current_layer, "OPFOR")
                promise_opfor = self.message_app_opfor.edit(content=f"{self.current_layer} TEAM 2", view=app_view_opfor, embed=app_view_opfor.embed)
                await promise_blufor
                await promise_opfor
        
        await promise_layer

    def run(self):
        return super().run(self.config["token"])
