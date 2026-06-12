from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.graph.state import Intent


class RecentMessage(BaseModel):
    role: str
    content: str


class ChatContext(BaseModel):
    selected_property_id: str | None = Field(default=None, alias="selectedPropertyId")
    recent_messages: list[RecentMessage] = Field(default_factory=list, alias="recentMessages")

    model_config = ConfigDict(populate_by_name=True)


class AgentChatRequest(BaseModel):
    user_id: str = Field(alias="userId")
    session_id: str | None = Field(default=None, alias="sessionId")
    message: str
    context: ChatContext = Field(default_factory=ChatContext)

    model_config = ConfigDict(populate_by_name=True)


class AgentChatResponse(BaseModel):
    intent: Intent
    answer: str
    properties: list[dict[str, Any]] = Field(default_factory=list)
    legal_cards: list[dict[str, Any]] = Field(default_factory=list, alias="legalCards")
    tool_results: dict[str, Any] = Field(default_factory=dict, alias="toolResults")
    next_actions: list[dict[str, Any]] = Field(default_factory=list, alias="nextActions")

    model_config = ConfigDict(populate_by_name=True)
