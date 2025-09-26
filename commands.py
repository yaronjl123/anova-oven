import dataclasses
import uuid
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import Field, BaseModel

from models import Cook


class Commands(Enum):
    SET_TEMP = "CMD_APO_SET_TEMPERATURE_UNIT"
    START = "CMD_APO_START"
    STOP = "CMD_APO_STOP"


@dataclasses.dataclass
class Payload:
    id: str
    type: Commands
    payload: Optional[Cook] = None


class Command(BaseModel):
    command: Commands
    payload: Payload
    requestId: UUID = Field(default_factory=uuid.uuid4)

    @classmethod
    def stop(cls, device_id):
        return cls(command=Commands.STOP,
                   payload=Payload(id=device_id,
                                   type=Commands.STOP))

    @classmethod
    def start(cls, device_id, cook: Cook):
        return cls(command=Commands.START,
                   payload=Payload(id=device_id,
                                   payload=cook,
                                   type=Commands.START))

        # @dataclasses.dataclass
        # class SetTemperature:
        # command = {
        #     "command": "CMD_APO_SET_TEMPERATURE_UNIT",
        #     "payload": {
        #         "id": self.selected_device["id"],
        #         "payload": {
        #             "temperatureUnit": unit
        #         },
        #         "type": "CMD_APO_SET_TEMPERATURE_UNIT"
        #     },
        #     "requestId": self.generate_uuid()
        # }
