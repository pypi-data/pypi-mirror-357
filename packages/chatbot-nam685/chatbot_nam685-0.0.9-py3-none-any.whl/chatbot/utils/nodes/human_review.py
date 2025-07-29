from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.types import Command, interrupt

from ..state import State


def human_review_node(state: State) -> Command[Literal["chatbot", "tools"]]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("The last message must be an AIMessage.")
    tool_call = last_message.tool_calls[-1]

    human_review = interrupt(
        {
            "question": "Is this correct?",
            "tool_call": tool_call,
        }
    )
    review_action = human_review["action"]
    review_data = human_review.get("data")

    if review_action == "feedback":
        tool_message = {
            "role": "tool",
            "content": review_data,
            "name": tool_call["name"],
            "tool_call_id": tool_call["id"],
        }
        return Command(goto="chatbot", update={"messages": [tool_message]})
    else:  # review_action == "continue":
        return Command(goto="tools")
