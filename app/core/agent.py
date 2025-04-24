# app/core/agent.py
from app.core.message_processor import MessageProcessor

# Create singleton instance
_message_processor = None

def get_message_processor():
    """Returns a singleton instance of the message processor"""
    global _message_processor
    if _message_processor is None:
        _message_processor = MessageProcessor()
    return _message_processor

# For backward compatibility
study_buddy_agent = get_message_processor()