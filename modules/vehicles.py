from datetime import datetime
from datetime import timedelta

class Vehicle():
    def __init__(self, name: str, respawn_time: int):
        self.name: str = name
        self.alive: bool = True
        self.respawn_time: int = respawn_time
        self.respawn_at: datetime = None

    def reset(self) -> None:
        if self.alive:
            self.respawn_at = datetime.now() + timedelta(seconds=self.respawn_time)
            self.alive = False
        else:
            self.respawn_at = None
            self.alive = True

def get_vehicle_dict_from_config(input_dict: dict) -> list[Vehicle]:
    result_list = []
    for key, value in input_dict.items():
        vehicle = Vehicle(key, value)
        if vehicle.respawn_time >= 300:
            result_list.append(vehicle)
    return result_list
