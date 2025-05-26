import asyncio
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add more verbose logging for specific modules
logging.getLogger('app.core.session_orchestrator').setLevel(logging.DEBUG)
logging.getLogger('app.core.sk.orchestrator.session_orchestrator').setLevel(logging.DEBUG)
logging.getLogger('app.api.session').setLevel(logging.DEBUG)

from app.models import db
from app.core.factory import get_factory
from app.core.vector_store import get_vector_store_client

async def test_session_creation():
    """Test creating a study session and track all steps"""
    print("=== Starting Session Creation Debug Test ===\n")
    
    # Get a database session
    db_session = next(db.get_db())
    
    # Get factory and orchestrator
    factory = get_factory()
    orchestrator = factory.get_session_orchestrator()
    
    # Get vector client
    vector_client = get_vector_store_client()
    
    topic = "Machine Learning Basics"
    user_id = "debug_user"
    duration_minutes = 15
    
    try:
        print(f"Creating session for topic: {topic}")
        print(f"User ID: {user_id}")
        print(f"Duration: {duration_minutes} minutes\n")
        
        # Create session
        session = await orchestrator.create_quick_session(
            user_id=user_id,
            topic=topic,
            duration_minutes=duration_minutes,
            db=db_session,
            vector_client=vector_client
        )
        
        print("\n=== Session Created Successfully ===")
        print(f"Session ID: {session['session_id']}")
        print(f"Status: {session['status']}")
        print(f"Number of activities: {len(session['activities'])}")
        
        print("\nActivities:")
        for i, activity in enumerate(session['activities']):
            print(f"  {i+1}. {activity['type']} - {activity['description']} ({activity['duration_minutes']} min)")
        
        # Try executing the first activity
        print("\n=== Executing First Activity ===")
        result = await orchestrator.execute_activity(
            session_id=session['session_id'],
            activity_index=0,
            db=db_session
        )
        
        print(f"Activity executed: {result['activity']['type']}")
        print(f"Next activity index: {result['next_activity_index']}")
        print(f"Session status: {result['status']}")
        
        return True
    except Exception as e:
        print(f"\n=== ERROR: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting debug session script...")
    success = asyncio.run(test_session_creation())
    if success:
        print("\nDebug session completed successfully")
    else:
        print("\nDebug session failed")
    print("=== Done ===") 