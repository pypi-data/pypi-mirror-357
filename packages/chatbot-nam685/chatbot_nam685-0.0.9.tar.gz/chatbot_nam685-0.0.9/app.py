from pprint import pprint

from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command

from .src.chatbot.graph import graph


def handle_human_review(event: dict, config: RunnableConfig):
    print(
        "================================= Human Review ================================="
    )
    print("Verifying tool call: ", event["__interrupt__"][0].value["question"])
    print("Tool Call:")
    pprint(event["__interrupt__"][0].value["tool_call"])
    action_input = input("Human Review - Action (feedback/continue): ")
    if action_input not in ["feedback", "continue"]:
        raise RuntimeError("Invalid action. Please enter 'feedback', or 'continue'.")
    data_input = input("Human Review - Data (optional): ")
    command: Command = Command(
        resume={
            "action": action_input,
            "data": data_input if data_input else None,
        }
    )
    stream_graph_updates(command, config)


def stream_graph_updates(graph_input: dict | Command, config: RunnableConfig):
    events = graph.stream(
        graph_input,
        config,
        stream_mode="values",
    )
    for event in events:
        if "__interrupt__" in event:
            handle_human_review(event, config)
        elif "messages" in event:
            event["messages"][-1].pretty_print()
            snapshot = graph.get_state(config)
            print("Sensitive: ", snapshot.values.get("sensitive", False))


config: RunnableConfig = {"configurable": {"thread_id": "1"}}

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        graph_input = {"messages": [{"role": "user", "content": user_input}]}
        stream_graph_updates(graph_input, config)
