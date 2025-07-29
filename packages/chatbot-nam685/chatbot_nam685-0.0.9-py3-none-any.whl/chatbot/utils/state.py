from langgraph.graph import MessagesState


class State(MessagesState):
    sensitive: bool  # Indicates certain topics (politics, sexual themes,...)
