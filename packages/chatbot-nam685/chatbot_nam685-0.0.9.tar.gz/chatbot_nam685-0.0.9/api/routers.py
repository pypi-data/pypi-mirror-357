import os
from typing import Any

from fastapi import APIRouter
from langgraph_sdk import get_client

from .models import ChatMessage, HumanReview, Thread

router = APIRouter()
langgraph_client = get_client(
    url=os.getenv("LANGGRAPH_API_URI", "http://langgraph-api:8000")
)


def parse_ai_response(
    ai_response: list[dict] | dict[str, Any],
) -> dict[str, Any]:
    if (
        not isinstance(ai_response, dict)
        or not {"__interrupt__", "messages"} & ai_response.keys()
    ):
        raise ValueError(
            "Unexpected response format from LangGraph API. Expected a dictionary with key 'messages' or '__interrupt__'."
        )
    if "__interrupt__" in ai_response:
        return {
            "type": "interrupt",
            "data": ai_response["__interrupt__"][-1]["value"]["tool_call"]["args"][
                "query"
            ],
        }
    return {"type": "message", "data": ai_response["messages"][-1]["content"]}


@router.get("/")
async def read_main() -> dict:
    return {"msg": "Hello! Welcome to the LangGraph Chat API"}


@router.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


@router.get("/chat")
async def list_chat_threads() -> list[Thread]:
    threads_data = await langgraph_client.threads.search(
        metadata={"graph_id": "chat"},
    )
    return [
        Thread(thread_id=thread["thread_id"], status=thread["status"])
        for thread in threads_data
    ]


@router.get("/chat/{thread_id}")
async def get_chat_history(thread_id: str) -> dict[str, list[str]]:
    thread_data = await langgraph_client.threads.get(thread_id=thread_id)
    if not isinstance(thread_data["values"], dict):
        raise ValueError(
            "Unexpected response format from LangGraph API. Expected a dictionary with key 'values'."
        )
    return {
        "history": [
            message["content"]
            for message in thread_data["values"]["messages"]
            if message["type"] in ["human", "ai"] and message["content"] != ""
        ]
    }


@router.get("/chat/{thread_id}/debug")
async def get_chat_history_debug(thread_id: str):
    return await langgraph_client.threads.get(thread_id=thread_id)


@router.post("/chat/{thread_id}")
async def chat_with_thread(thread_id: str, message: ChatMessage) -> dict[str, Any]:
    ai_response = await langgraph_client.runs.wait(
        thread_id=thread_id,
        assistant_id="chat",
        input={"messages": [{"role": "user", "content": message.text}]},
        if_not_exists="create",
    )
    return parse_ai_response(ai_response)


@router.post("/chat/{thread_id}/human_review")
async def human_review(thread_id: str, review: HumanReview) -> dict[str, Any]:
    ai_response = await langgraph_client.runs.wait(
        thread_id=thread_id,
        assistant_id="chat",
        command={
            "resume": {
                "action": review.action,
                "data": review.data,
            }
        },
    )
    return parse_ai_response(ai_response)


@router.delete("/chat/{thread_id}")
async def delete_chat_thread(thread_id: str) -> dict[str, Any]:
    await langgraph_client.threads.delete(thread_id=thread_id)
    return {"success": True, "thread_id": thread_id}
