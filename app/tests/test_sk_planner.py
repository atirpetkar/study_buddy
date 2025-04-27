# app/tests/test_sk_planner.py
import asyncio
import sys
import os
import json

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.sk.planners.study_planner import SKStudyPlanGenerator

async def test_sk_planner():
    """Test the SK study planner"""
    # Create a test progress data
    progress_data = {
        "user_id": "test_user",
        "topics": {
            "Machine Learning": {
                "proficiency": 0.3,
                "confidence": 0.4,
                "last_interaction": "2025-04-20T00:00:00"
            },
            "Data Structures": {
                "proficiency": 0.7,
                "confidence": 0.6,
                "last_interaction": "2025-04-25T00:00:00"
            },
            "Neural Networks": {
                "proficiency": 0.5,
                "confidence": 0.5, 
                "last_interaction": "2025-04-15T00:00:00"
            }
        }
    }
    
    # Create the planner
    planner = SKStudyPlanGenerator()
    
    # Generate a plan
    print("Generating study plan...")
    plan = await planner.generate_plan(None, "test_user", progress_data)
    
    # Print the plan
    print("\nGenerated Study Plan:")
    print(json.dumps(plan, indent=2))

if __name__ == "__main__":
    asyncio.run(test_sk_planner())