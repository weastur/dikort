from pydantic import BaseModel, validator
import typing


class Rules(BaseModel):
    max_length: int

    @validator("max_length")
    def max_length_min(self, value):
        if value < 1:
            raise ValueError("max_length must be greater than 0")
        return value


class Config(BaseModel):

    default_rules: Rules
