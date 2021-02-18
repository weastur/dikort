from pydantic import BaseModel, validator


class Rules(BaseModel):
    max_length: int

    @validator("max_length")
    def max_length_min(self, length):
        if length < 1:
            raise ValueError("max_length must be greater than 0")
        return length


class Config(BaseModel):

    default_rules: Rules
