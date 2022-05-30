from distutils.command.config import config
from discord import ButtonStyle
from discord import Embed
from time import mktime
from discord.ui import Button
from discord.interactions import Interaction
from discord.ui import View
from modules.config_utils import get_config
from modules.vehicles import Vehicle
from modules.vehicles import get_vehicle_dict_from_config

layers_config_path: str = "./modules/layers.json"
config_path: str = "./modules/config.json"

layers: dict = get_config(layers_config_path)
cfg: dict = get_config(config_path)
players_whitelisted: list[str] = cfg["button_whitelist"]
special_whitelist: list[str] = cfg["special_whitelist"]

class MessageView(View):
    def __init__(self, layer_name:str, side: str):
        super().__init__(timeout=None)
        self.embed: VehicleEmbed = VehicleEmbed(layer_name, side)
        self.layer_name = layer_name
        self.layer = layers[layer_name]
        vehicles = get_vehicle_dict_from_config(self.layer[side]["vehicles"])
        vehicles.sort(key=lambda x: x.respawn_time, reverse=True)
        for vehicle in vehicles:
            self.add_item(VehicleButton(vehicle))

class VehicleButton(Button):
    def __init__(self, vehicle: Vehicle):
        super().__init__(label=vehicle.name, style=ButtonStyle.green)
        self.vehicle: Vehicle = vehicle
        self.index: int = None

    def reset(self):
        self.vehicle.reset()
        if self.vehicle.alive:
            self.style = ButtonStyle.green
        else:
            self.style = ButtonStyle.danger

    async def callback(self, interaction: Interaction):
        print(interaction.user.id)
        if interaction.user.voice is None:
            return
        if not str(interaction.user) in players_whitelisted:
            if not str(interaction.user.id)[:4] in special_whitelist:
                return
        assert self.view is not None
        view: MessageView = self.view
        self.reset()
        if self.vehicle.alive:
            view.embed.remove_field(self.index)
            view.embed.vehicle_list.pop(self.index)
            self.index = None
        else:
            self.index = len(view.embed.vehicle_list)
            view.embed.vehicle_list.append(self)
            view.embed.insert_field_at(index=self.index, name=self.vehicle.name, value=f"<t:{str(mktime(self.vehicle.respawn_at.timetuple()))[:10]}:R>", inline=True)
        
        view.embed.update_indexes()
        # self.view.update_view()
        await interaction.response.edit_message(view=self.view, embed=view.embed)

class VehicleEmbed(Embed):
    def __init__(self, layer: str, side: str):
        self.vehicle_list: list[VehicleButton] = []
        if side == "BLUEFOR":
            color: int = 0x4251f5
        else:
            color: int = 0xad0202
        super().__init__(title=layers[layer][side]["faction"], color=color)

    def update_indexes(self):
        i: int = 0
        for vehicleButton in self.vehicle_list:
            vehicleButton.index = i
            i += 1

class ServerButtonView(View):
    def __init__(self, button_names: list[str], client):
        super().__init__(timeout=None)
        self.client = client
        for i in range(len(button_names)):
            self.add_item(ServerButton(button_names[i], i))
    
    def update_buttons(self):
        buttons: list[ServerButton] = self.children
        for button in buttons:
            button.disabled = False
            button.style = ButtonStyle.secondary

class ServerButton(Button):
    def __init__(self, name: str, id: int):
        super().__init__(label=name, style=ButtonStyle.secondary)
        self.id = id
        if self.id == 0:
            self.disabled = True
            self.style = ButtonStyle.primary
        
    async def callback(self, interaction: Interaction):
        print(interaction.user.id)
        if interaction.user.voice is None:
            return
        if not str(interaction.user) in players_whitelisted:
            if not str(interaction.user.id)[:4] in special_whitelist:
                return
        assert self.view is not None
        view: ServerButtonView = self.view
        view.client.selected_server = self.id
        view.update_buttons()
        self.disabled = True
        self.style = ButtonStyle.primary

        await interaction.response.edit_message(view=view)
