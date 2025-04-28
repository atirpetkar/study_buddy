# app/tests/test_session_orchestrator.py
import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.sk.orchestrator.session_orchestrator import SKSessionOrchestrator

async def test_session_orchestrator():
    """Test the SK session orchestrator"""
    # Create orchestrator
    orchestrator = SKSessionOrchestrator()
    
    # Test session planning
    print("\n===== Testing Quick Session Creation =====")
    plan = await orchestrator.create_quick_session(
        user_id="test_user",
        topic="Machine Learning Fundamentals",
        duration_minutes=15
    )
    
    print(f"Session plan created with ID: {plan['session_id']}")
    print(f"Number of activities: {len(plan['activities'])}")
    print("\nActivities:")
    for i, activity in enumerate(plan['activities']):
        print(f"{i+1}. {activity['type']} - {activity['description']} ({activity['duration_minutes']} min)")
    
    # Test activity execution
    print("\n===== Testing Activity Execution =====")
    result = await orchestrator.execute_activity(
        session_id=plan['session_id'],
        activity_index=0
    )
    
    print(f"Activity executed: {result['activity']['type']}")
    print(f"Result snippet: {result['result'][:100]}...")  # Show first 100 chars
    print(f"Next activity index: {result['next_activity_index']}")
    print(f"Session status: {result['status']}")
    
    print("\nSession orchestrator test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_session_orchestrator())