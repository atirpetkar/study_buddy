#!/bin/bash

# Create sk directory structure
mkdir -p sk/skills sk/connectors sk/planners

# Create __init__.py files for all directories
touch sk/__init__.py
touch sk/skills/__init__.py
touch sk/connectors/__init__.py
touch sk/planners/__init__.py

# Create factory file in core directory
touch factory.py

# Create core SK files
touch sk/kernel_factory.py

# Create connector files
touch sk/connectors/processor_adapter.py
touch sk/connectors/model_connector.py

# Create skill files
touch sk/skills/quiz_skill.py
touch sk/skills/flashcard_skill.py
touch sk/skills/tutor_skill.py
touch sk/skills/personalization_skill.py

# Create planner files
touch sk/planners/study_planner.py

