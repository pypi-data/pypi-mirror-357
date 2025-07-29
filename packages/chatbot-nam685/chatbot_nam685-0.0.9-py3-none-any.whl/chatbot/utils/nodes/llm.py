from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from ..state import State
from ..tools.multiply import multiply
from ..tools.search import search

llm = init_chat_model("gpt-4o-mini")
llm_with_tools = llm.bind_tools([multiply, search])


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def classify_sensitivity(state: State) -> dict[str, bool]:
    prompt = [
        SystemMessage(
            content="Determine if the conversation topic is sensitive (political, sexual theme,...). Return True or False."
        ),
        state["messages"][-1],
        HumanMessage(content="Is this topic sensitive? Respond with True or False."),
    ]
    response = llm.invoke(prompt)
    sensitive = response.text().strip().lower() == "true"
    return {"sensitive": sensitive}


tool_node = ToolNode(tools=[multiply, search], name="tools")
