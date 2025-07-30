from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings

from askui.models.shared.computer_agent import ComputerAgentSettingsBase
from askui.models.shared.settings import ChatCompletionsCreateSettings

COMPUTER_USE_BETA_FLAG = "computer-use-2024-10-22"


class AnthropicSettings(BaseSettings):
    api_key: SecretStr = Field(
        default=...,
        min_length=1,
        validation_alias="ANTHROPIC_API_KEY",
    )


class ClaudeSettingsBase(BaseModel):
    anthropic: AnthropicSettings = Field(default_factory=lambda: AnthropicSettings())


class ClaudeSettings(ClaudeSettingsBase):
    resolution: tuple[int, int] = Field(default_factory=lambda: (1280, 800))
    chat_completions_create_settings: ChatCompletionsCreateSettings = Field(
        default_factory=ChatCompletionsCreateSettings,
        description="Settings for ChatCompletions",
    )


class ClaudeComputerAgentSettings(ComputerAgentSettingsBase, ClaudeSettingsBase):
    pass
