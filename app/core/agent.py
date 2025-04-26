# app/core/agent.py
from app.core.factory import get_factory
from app.core.message_processor import MessageProcessor

# Get the factory
factory = get_factory()

def get_message_processor() -> MessageProcessor:
    """Returns a factory-provided message processor"""
    return factory.get_message_processor()

# For backward compatibility
study_buddy_agent = get_message_processor()

