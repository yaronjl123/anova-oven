import dataclasses
import uuid
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class BulbModes(str, Enum):
    DRY = "dry"
    WET = "wet"


@dataclasses.dataclass
class HeatingElements:
    @dataclasses.dataclass
    class STATE:
        on: bool

    top: STATE
    bottom: STATE
    rear: STATE

    def is_bottom_only(self):
        return self.bottom.on and not self.top.on and not self.rear.on

    @classmethod
    def top_only(cls):
        return cls(bottom=HeatingElements.STATE(on=False),
                   top=HeatingElements.STATE(on=True),
                   rear=HeatingElements.STATE(on=False))

    @classmethod
    def rear_only(cls):
        return cls(bottom=HeatingElements.STATE(on=False),
                   top=HeatingElements.STATE(on=False),
                   rear=HeatingElements.STATE(on=True))

    @classmethod
    def bottom_only(cls):
        return cls(bottom=HeatingElements.STATE(on=True),
                   top=HeatingElements.STATE(on=False),
                   rear=HeatingElements.STATE(on=False))

    @classmethod
    def top_and_rear(cls):
        return cls(bottom=HeatingElements.STATE(on=False),
                   top=HeatingElements.STATE(on=True),
                   rear=HeatingElements.STATE(on=True))

    @classmethod
    def top_and_bottom(cls):
        return cls(bottom=HeatingElements.STATE(on=True),
                   top=HeatingElements.STATE(on=True),
                   rear=HeatingElements.STATE(on=False))


class TimerStartType(str, Enum):
    IMMEDIATELY = "immediately"
    WHEN_PREHEATED = "when-preheated"
    MANUAL = "manual"
    ON_DETECTION = "on-detection"


@dataclasses.dataclass
class TempSetPoint:
    class SetPoint(BaseModel):
        celsius: float = Field(ge=25, le=250)

    setpoint: SetPoint


@dataclasses.dataclass
class TempBulb:
    mode: BulbModes
    dry: TempSetPoint = None
    wet: TempSetPoint = None

    @model_validator(mode='after')
    def check_mutual_exclusivity(self) -> 'TempBulb':
        if self.mode == BulbModes.DRY and (self.wet is not None or self.dry is None):
            raise ValueError(f"bad dry temp settings")
        if self.mode == BulbModes.WET and (self.dry is not None or self.wet is None):
            raise ValueError(f"bad wet temp settings")
        if self.mode == BulbModes.WET and (self.wet.setpoint.celsius > 100 or self.wet.setpoint.celsius < 25):
            raise ValueError(f"temp must be between 25-100 C when in sous vide mode")
        return self

    @classmethod
    def wet_bulb(cls, temp: float):
        return cls(mode=BulbModes.WET,
                   wet=TempSetPoint(setpoint=TempSetPoint.SetPoint(celsius=temp)))

    @classmethod
    def dry_bulb(cls, temp: float):
        return cls(mode=BulbModes.DRY,
                   dry=TempSetPoint(setpoint=TempSetPoint.SetPoint(celsius=temp)))


class Fan(BaseModel):
    speed: int = Field(ge=0, le=100)


@dataclasses.dataclass
class Vent:
    open: bool = False


class SteamMode(str, Enum):
    IDLE = "idle"
    RELATIVE = "relative-humidity"
    PERCENTAGE = "steam-percentage"


class SteamSetPoint(BaseModel):
    setpoint: int = Field(ge=0, le=100)


@dataclasses.dataclass
class SteamGenerators:
    mode: SteamMode
    relativeHumidity: SteamSetPoint

    @classmethod
    def sous_vide(cls, steam_percentage):
        return cls(mode=SteamMode.RELATIVE, relativeHumidity=SteamSetPoint(setpoint=steam_percentage))

    @classmethod
    def no_steam(cls):
        return cls(mode=SteamMode.IDLE, relativeHumidity=SteamSetPoint(setpoint=0))


class Probe(BaseModel):
    class SetPoint(BaseModel):
        celsius: float = Field(ge=1, le=100)

    setpoint: SetPoint

    def __init__(self, temp: float):
        super().__init__(setpoint=self.SetPoint(celsius=temp))


    # def __dict__(self):
    #     return


class Stage(BaseModel):
    class Type(str, Enum):
        PREHEAT = "preheat"
        COOK = "cook"

    class Transition(str, Enum):
        AUTO = "automatic"
        MANUAL = "manual"

    id: UUID = Field(default_factory=uuid.uuid4)
    title: str
    description: str
    type: Type
    userActionRequired: bool
    temperatureBulbs: TempBulb
    heatingElements: HeatingElements
    fan: Fan
    rackPosition: int = Field(default=3, ge=1, le=5)
    probe: Probe
    stageTransitionType: Transition
    steamGenerators: SteamGenerators
    probeAdded: bool = False
    timerStartOnDetect: bool = False
    vent: Vent = Field(default_factory=Vent)
    stepType: str = "stage"

    @model_validator(mode='after')
    def check_mutual_exclusivity(self) -> 'Stage':
        if self.heatingElements.is_bottom_only() and self.temperatureBulbs.dry.setpoint.celsius > 180:
            raise ValueError(f"Temperature can't exceed 180 when bottom element only")

        return self

    #TODO - add fan at 100 check for steam
    #TODO - checl probAdded
    #TOdO - handle timers


class Cook(BaseModel):
    stages: list[Stage]
    cookId: UUID = Field(default_factory=uuid.uuid4)
    originSource: str = "api"
    # type:
