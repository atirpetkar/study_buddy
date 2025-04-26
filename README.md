# Study Buddy Agent

An intelligent, personalized AI tutor that adapts to your learning style and helps you master educational content effectively.

## Features

- **Document Processing** - Upload your study materials for AI analysis
- **Interactive Tutoring** - Engage in Socratic dialogue to deepen understanding
- **Quiz Generation** - Create custom quizzes to test knowledge
- **Flashcard System** - Generate and review flashcards with spaced repetition
- **Personalization** - Content adapted to your learning style and progress
- **Study Planning** - Get personalized study plans based on your progress

## Installation

### Prerequisites

- Python 3.9+
- Git
- [GitHub Token](https://github.com/settings/tokens) with access to model inference

### Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/study-buddy-agent.git
cd study-buddy-agent
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
# Linux/Mac
export GITHUB_TOKEN="your_github_token"
export ENDPOINT="https://models.inference.ai.azure.com"
export GITHUB_MODEL="openai/gpt-4o"

# Windows
set GITHUB_TOKEN=your_github_token
set ENDPOINT=https://models.inference.ai.azure.com
set GITHUB_MODEL=openai/gpt-4o
```

5. Initialize the database:

```bash
python -m app.models.create_tables
```

6. Start the application:

```bash
uvicorn main:app --reload
```

## Usage

### API Endpoints

The application exposes the following API endpoints:

- **Document Processing**: `/vectorstore/upload` - Upload documents for processing
- **Chat**: `/chat/chat` - Chat with the agent about documents
- **Quiz Generation**: `/quiz/generate` - Generate quizzes on specific topics
- **Flashcards**: `/flashcard/generate` - Create flashcards for a topic
- **Tutoring**: Use mode="tutor" with the chat endpoint
- **Personalization**: `/personalization/learning-style/{user_id}` - Get personalized learning strategies
- **Study Planning**: `/study-plan/advanced` - Get personalized study plans

### Testing

Run the comprehensive test suite:

```bash
python app/tests/integration_tests.py
```

Or test specific components:

```bash
python app/tests/test_flashcard.py
python app/tests/test_day4_quiz.py
```

### Demo Script

We provide a demo script to showcase the agent's capabilities:

```bash
python demo_script.py
```

## Architecture

### Core Components

- **Vector Store**: FAISS-based semantic search for document content
- **Message Processor**: Handles interactions with LLMs
- **Quiz Generator**: Creates quizzes based on document content
- **Flashcard Generator**: Generates flashcards with spaced repetition
- **Tutoring System**: Manages Socratic tutoring sessions
- **Personalization Engine**: Analyzes and adapts to learning styles
- **Progress Tracker**: Monitors learning progress across topics
- **Study Planner**: Creates personalized study plans

### Data Flow

1. Documents are uploaded, processed, and stored in the vector database
2. User interacts with the agent through various modes (chat, quiz, etc.)
3. Agent retrieves relevant context from the vector store
4. Models generate responses based on context and user queries
5. Progress is tracked and used to personalize future interactions
6. Learning style is detected and used to adapt content presentation

## Performance Optimizations

- **Enhanced Chunking**: Improved document segmentation that respects semantic boundaries
- **Caching**: Embedding cache for frequently used text
- **Result Deduplication**: Removes duplicate context chunks for better responses
- **Response Time Monitoring**: Tracks component performance to identify bottlenecks

## Future Enhancements

We plan to add the following features in future updates:

- **Multi-modal Learning**: Support for images and diagrams
- **Collaborative Learning**: Peer-to-peer learning integration
- **Advanced Visualization**: Generated charts and diagrams
- **Mobile Support**: Native mobile applications
- **Expanded Progress Analytics**: More detailed learning insights

## License

[MIT License](LICENSE)

## Acknowledgments

- Developed for the Agent Hackathon
- Uses Microsoft's Semantic Kernel and AutoGen for agent capabilities
- Built with FastAPI, SQLite, and FAISS

## Contributors

- Atir Petkar - Lead Developer


## Contact

For any questions or feedback, please open an issue on GitHub or contact me at: atirpetkar10@gmail.com