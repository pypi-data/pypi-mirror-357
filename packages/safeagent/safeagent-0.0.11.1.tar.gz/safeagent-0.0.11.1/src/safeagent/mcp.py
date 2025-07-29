# src/safeagent/mcp.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import uuid

@dataclass
class Message:
    """
    Represents a single message sent between agents.
    """
    # Non-default arguments should come first
    sender_id: str
    recipient_id: str
    content: Any
    # Default arguments or arguments with default_factory come after
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_response: bool = False
    request_id: Optional[str] = None 

@dataclass
class AgentMailbox:
    """
    Holds incoming messages for a specific agent.
    """
    messages: List[Message] = field(default_factory=list)

# Message for Agent-to-Agent Communication

class MessageBus:
    """
    A central dispatcher for routing messages between registered agents.
    This provides a decoupled way for agents to communicate.
    """
    def __init__(self):
        # agent_id -> AgentMailbox
        self._mailboxes: Dict[str, AgentMailbox] = {}
        print("MessageBus initialized.")

    def register_agent(self, agent_id: str):
        """
        Registers an agent with the message bus, creating a mailbox for it.
        """
        if agent_id not in self._mailboxes:
            self._mailboxes[agent_id] = AgentMailbox()
            print(f"Agent '{agent_id}' registered with MessageBus.")
        else:
            print(f"Agent '{agent_id}' is already registered.")

    def send_message(self, message: Message):
        """
        Sends a message to the recipient agent's mailbox.
        """
        recipient_id = message.recipient_id
        if recipient_id not in self._mailboxes:
            raise ValueError(f"Recipient agent '{recipient_id}' not registered with the message bus.")
        
        self._mailboxes[recipient_id].messages.append(message)
        print(f"Message from '{message.sender_id}' sent to '{recipient_id}'.")

    def get_messages(self, agent_id: str) -> List[Message]:
        """
        Retrieves all messages from an agent's mailbox and clears it.
        """
        if agent_id not in self._mailboxes:
            raise ValueError(f"Agent '{agent_id}' not registered with the message bus.")
        
        messages = self._mailboxes[agent_id].messages
        self._mailboxes[agent_id].messages = [] 
        if messages:
            print(f"Agent '{agent_id}' retrieved {len(messages)} message(s).")
        return messages