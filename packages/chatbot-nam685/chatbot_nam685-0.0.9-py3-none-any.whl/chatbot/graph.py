from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from chatbot.utils.nodes.human_review import human_review_node
from chatbot.utils.nodes.llm import (
    chatbot,
    classify_sensitivity,
    tool_node,
)
from chatbot.utils.state import State

load_dotenv()


def route_after_chatbot(state: State) -> Literal[END, "human_review", "tools"]:  # type: ignore
    ai_message = state["messages"][-1]
    if not isinstance(ai_message, AIMessage):
        raise ValueError("The last message must be an AIMessage.")
    if len(ai_message.tool_calls) == 0:
        return END
    elif state["sensitive"]:
        return "human_review"
    else:
        return "tools"


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("human_review", human_review_node)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("classify_sensitivity", classify_sensitivity)

graph_builder.add_edge(START, "classify_sensitivity")
graph_builder.add_edge("classify_sensitivity", "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    route_after_chatbot,
)
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()

graph.get_graph().print_ascii()
