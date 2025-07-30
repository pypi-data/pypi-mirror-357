from pydantic import BaseModel, Field, model_validator
from typing import Annotated, List, Literal, Optional, Self, Union
from enum import Enum


class VolumeQuantity(str, Enum):
    duration = "duration"
    distance = "distance"


class IntensityQuantity(str, Enum):
    speed = "speed"
    power = "power"

class RepeatQuantity(str, Enum):
    NUMBER = "number"


class Reference(str, Enum):
    absolute = "absolute"
    tte = "tte"
    parameter = "parameter"


class Value(BaseModel):
    """Represents a value with its reference type"""
    reference: Reference
    value: Union[int, float]
    parameter: Optional[str] = None  # Required when reference="parameter"
    
    @model_validator(mode="after")
    def validate_parameter(self) -> Self:
        if self.reference == Reference.parameter and not self.parameter:
            raise ValueError("parameter is required when reference='parameter'")
        if self.reference != Reference.parameter and self.parameter:
            raise ValueError("parameter should only be set when reference='parameter'")
        return self


class ConstantValue(BaseModel):
    type: Literal["constant"] = "constant"
    quantity: Union[VolumeQuantity, IntensityQuantity, RepeatQuantity]
    value: Value


class RangeValue(BaseModel):
    type: Literal["range"] = "range"
    quantity: Union[VolumeQuantity, IntensityQuantity, RepeatQuantity]
    min: Optional[Value] = None
    max: Optional[Value] = None
    
    @model_validator(mode="after")
    def validate_bounds(self) -> Self:
        if not self.min and not self.max:
            raise ValueError("At least one of min or max must be specified")
        return self


class RampValue(BaseModel):
    type: Literal["ramp"] = "ramp"
    quantity: Union[VolumeQuantity, IntensityQuantity, RepeatQuantity]
    start: Value
    end: Value


class Instruction(BaseModel):
    type: Literal["instruction"] = "instruction"
    text: str


class Interval(BaseModel):
    type: Literal["interval"] = "interval"
    volume: Union[ConstantValue, RangeValue, RampValue] = Field(..., discriminator="type")
    intensity: Union[ConstantValue, RangeValue, RampValue] = Field(..., discriminator="type")
    
    @model_validator(mode="after")
    def validate_quantities(self) -> Self:
        # Validate volume quantity
        if self.volume.quantity not in [VolumeQuantity.duration, VolumeQuantity.distance]:
            raise ValueError(f"Volume quantity must be 'duration' or 'distance', got '{self.volume.quantity}'")
        
        # Validate intensity quantity  
        if self.intensity.quantity not in [IntensityQuantity.speed, IntensityQuantity.power]:
            raise ValueError(f"Intensity quantity must be 'speed' or 'power', got '{self.intensity.quantity}'")
        
        return self


class Repeat(BaseModel):
    type: Literal["repeat"]
    count: Union[ConstantValue, RangeValue] = Field(..., discriminator="type")
    content: List[Union[Interval, "Repeat", Instruction]]
    
    @model_validator(mode="after")
    def validate_count_quantity(self) -> Self:
        # Validate count quantity
        if self.count.quantity != RepeatQuantity.NUMBER:
            raise ValueError(f"Repeat count quantity must be 'number', got '{self.count.quantity}'")
        return self


class Section(BaseModel):
    type: Literal["section"] = "section"
    name: Optional[str]
    content: List[Union[Interval, Repeat, Instruction]]


WorkoutContent = Annotated[
    Union[Interval, Repeat, Section, Instruction],
    Field(discriminator="type")
]


class BaseWorkout(BaseModel):
    version: str = "0.1.0"
    title: str | None = None
    description: str | None = None
    content: List[WorkoutContent]

    def model_dump_json(self, *args, **kwargs) -> str:
        """
        Exclude unset fields from the JSON output to keep the format clean.
        """
        kwargs["exclude_unset"] = True
        kwargs["exclude_none"] = True
        return super().model_dump_json(*args, **kwargs)