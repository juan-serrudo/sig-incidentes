"""Only the initial request message is accepted, not its resolution or category."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=20, max_length=2000, strict=True)

    @field_validator("message")
    @classmethod
    def meaningful_message(cls, value):
        cleaned = " ".join(value.split())
        if len(cleaned) < 20 or sum(character.isalpha() for character in cleaned) < 10:
            raise ValueError("Describe the request with at least 20 characters and 10 letters.")
        return cleaned

