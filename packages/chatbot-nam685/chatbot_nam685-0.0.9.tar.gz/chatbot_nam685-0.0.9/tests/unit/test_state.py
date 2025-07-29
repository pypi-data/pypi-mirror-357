from langchain_core.messages import AIMessage, HumanMessage

from chatbot.utils.state import State


def test_state_accepts_valid_messages():
    valid_messages = [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!"),
    ]
    state = State(messages=valid_messages, sensitive=False)
    assert state["messages"] == valid_messages
