"""Input schemas for technological incident triage.

Strict validation forbids leaking fields such as category, resolution, or assignee.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IncidentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=5, max_length=200, strict=True)
    initial_description: str = Field(min_length=15, max_length=2000, strict=True)

    @field_validator("title")
    @classmethod
    def meaningful_title(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 5 or sum(character.isalpha() for character in cleaned) < 3:
            raise ValueError("Title must contain at least 5 characters and 3 letters.")
        return cleaned

    @field_validator("initial_description")
    @classmethod
    def meaningful_description(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 15 or sum(character.isalpha() for character in cleaned) < 10:
            raise ValueError("Description must contain at least 15 characters and 10 letters.")
        return cleaned

    def combined_text(self) -> str:
        return f"{self.title}. {self.initial_description}"


# Alias for backward compatibility
TicketInput = IncidentInput
