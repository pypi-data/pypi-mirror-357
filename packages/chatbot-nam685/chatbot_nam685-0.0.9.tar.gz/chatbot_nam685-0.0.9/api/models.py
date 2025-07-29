from pydantic import BaseModel


class ChatMessage(BaseModel):
    text: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hello",
                }
            ]
        }
    }


class HumanReview(BaseModel):
    action: str
    data: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "action": "feedback",
                    "data": "That's not what I meant! Please try again.",
                },
                {
                    "action": "continue",
                    "data": "",
                },
            ]
        }
    }


class Thread(BaseModel):
    thread_id: str
    status: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "thread_id": "ffbbe00c-c65d-437e-892d-a4b59120e3c9",
                    "status": "idle",
                },
            ]
        }
    }
