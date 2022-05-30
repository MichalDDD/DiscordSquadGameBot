from datetime import datetime
from discord import Embed
from a2s import SourceInfo

class ServerEmbed(Embed):
    def __init__(self, sourceInfoList: list[SourceInfo]):
        super().__init__(color=0xf542e3, timestamp=datetime.now())
        # server name
        for sourceInfo in sourceInfoList:
            self.add_field(name="Server Name", value=sourceInfo.server_name, inline=True)
        
        # layer name
        for sourceInfo in sourceInfoList:
            self.add_field(name="Layer", value=sourceInfo.map_name, inline=True)
        
        # player count
        for sourceInfo in sourceInfoList:
            self.add_field(name="Players", value=f"{min(sourceInfo.player_count, 100)} / {sourceInfo.max_players}", inline=True)

        # queue
        for sourceInfo in sourceInfoList:
            self.add_field(name="Queue", value=max(sourceInfo.player_count - 100, 0), inline=True)


        # ping
        for sourceInfo in sourceInfoList:
            self.add_field(name="Ping", value=int(sourceInfo.ping * 1000), inline=True)

        