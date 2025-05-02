import json
from typing import List, Dict
from pydantic import BaseModel, Field
from pathlib import Path

MEMORY_FILE = Path("memory/shared.json")
MEMORY_FILE.parent.mkdir(exist_ok=True)

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class SharedMemory(BaseModel):
    messages: List[Message] = Field(default_factory=list)

    def append(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))

    def to_chat_input(self) -> List[Dict[str, str]]:
        return [msg.dict() for msg in self.messages]

    def clear(self):
        self.messages.clear()

    def save(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.dict(), f, indent=2)

    @classmethod
    def load(cls) -> "SharedMemory":
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                return cls(**data)
        except FileNotFoundError:
            return cls()

class SharedMemoryManager:
    def __init__(self):
        self.memory: SharedMemory = SharedMemory.load()

    def append_user(self, content: str):
        self.memory.append("user", content)
        self.memory.save()

    def append_assistant(self, content: str):
        self.memory.append("assistant", content)
        self.memory.save()

    def get_chat_input(self) -> List[Dict[str, str]]:
        return self.memory.to_chat_input()

    def reset(self):
        self.memory.clear()
        self.memory.save()
