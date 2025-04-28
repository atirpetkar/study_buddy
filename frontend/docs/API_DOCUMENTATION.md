# API Documentation: AI-Powered Study Buddy

This document provides detailed documentation for the backend API endpoints of the AI-Powered Study Buddy application. Use this as a reference when integrating with the API or extending its functionality.

## Base URL

All API endpoints are relative to the base URL: `/api`

## Authentication

Authentication is not fully implemented in the current version. A user ID is required for many endpoints but is not validated against any authentication token. In a production environment, proper authentication would need to be implemented.

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "message": "Error description",
  "errors": {
    "field1": ["Error details for field1"],
    "field2": ["Error details for field2"]
  }
}
```

Status codes:
- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## API Endpoints

### Document Management

#### Upload Documents

Uploads one or more documents to be processed and stored.

- **URL**: `/vectorstore/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `files`: Array of files to upload (form data)

**Example Request**:
```bash
curl -X POST \
  http://localhost:5000/api/vectorstore/upload \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@document1.pdf' \
  -F 'files=@document2.txt'
```

**Success Response (200 OK)**:
```json
{
  "status": "success",
  "total_chunks": 15,
  "files": [
    {
      "file": "document1.pdf",
      "chunks": 8,
      "metadatas": [
        { "chunk_index": 0, "length": 1000 },
        { "chunk_index": 1, "length": 1000 }
      ]
    },
    {
      "file": "document2.txt",
      "chunks": 7,
      "metadatas": [
        { "chunk_index": 0, "length": 1000 },
        { "chunk_index": 1, "length": 1000 }
      ]
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: No files uploaded
- `500 Internal Server Error`: Error uploading documents

#### Get All Documents

Retrieves all uploaded documents.

- **URL**: `/vectorstore/documents`
- **Method**: `GET`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/vectorstore/documents
```

**Success Response (200 OK)**:
```json
{
  "document_count": 2,
  "total_chunks": 15,
  "documents": [
    {
      "filename": "document1.pdf",
      "filetype": "pdf",
      "upload_time": "2025-04-28T10:30:00.000Z",
      "chunk_count": 8
    },
    {
      "filename": "document2.txt",
      "filetype": "txt",
      "upload_time": "2025-04-28T10:35:00.000Z",
      "chunk_count": 7
    }
  ]
}
```

**Error Response**:
- `500 Internal Server Error`: Error fetching documents

### Study Session Management

#### Create Quick Session

Creates a new study session with a balanced set of learning activities.

- **URL**: `/session/quick`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  - `user_id`: String - User identifier
  - `topic`: String - Topic for the study session
  - `duration_minutes`: Number - Total duration of the session in minutes

**Example Request**:
```bash
curl -X POST \
  http://localhost:5000/api/session/quick \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user123",
    "topic": "Neural Networks",
    "duration_minutes": 30
  }'
```

**Success Response (200 OK)**:
```json
{
  "session_id": "sess_a1b2c3",
  "user_id": "user123",
  "topic": "Neural Networks",
  "duration_minutes": 30,
  "created_at": "2025-04-28T11:00:00.000Z",
  "activities": [
    {
      "type": "introduction",
      "duration_minutes": 6,
      "description": "Introduction to Neural Networks",
      "parameters": { "topic": "Neural Networks" }
    },
    {
      "type": "flashcard",
      "duration_minutes": 9,
      "description": "Review key concepts in Neural Networks",
      "parameters": { "num_cards": 3, "topic": "Neural Networks" }
    },
    {
      "type": "quiz",
      "duration_minutes": 9,
      "description": "Test your knowledge of Neural Networks",
      "parameters": { "num_questions": 2, "difficulty": "medium", "topic": "Neural Networks" }
    },
    {
      "type": "summary",
      "duration_minutes": 6,
      "description": "Summarize what you've learned about Neural Networks",
      "parameters": { "topic": "Neural Networks" }
    }
  ],
  "status": "planned",
  "current_activity_index": 0
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Error creating study session

#### Execute Session Activity

Executes a single activity within a study session.

- **URL**: `/session/execute`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  - `session_id`: String - Session identifier
  - `activity_index`: Number - Index of the activity to execute

**Example Request**:
```bash
curl -X POST \
  http://localhost:5000/api/session/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "sess_a1b2c3",
    "activity_index": 0
  }'
```

**Success Response (200 OK)**:
```json
{
  "session_id": "sess_a1b2c3",
  "activity": {
    "type": "introduction",
    "duration_minutes": 6,
    "description": "Introduction to Neural Networks",
    "parameters": { "topic": "Neural Networks" }
  },
  "result": "Neural Networks is an important area of study that covers several key concepts...",
  "next_activity_index": 1,
  "status": "in_progress"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data or activity index
- `404 Not Found`: Session not found
- `500 Internal Server Error`: Error executing activity

#### Get User Sessions

Retrieves all study sessions for a given user.

- **URL**: `/session/user/:user_id`
- **Method**: `GET`
- **URL Parameters**:
  - `user_id`: String - User identifier

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/session/user/user123
```

**Success Response (200 OK)**:
```json
[
  {
    "session_id": "sess_a1b2c3",
    "user_id": "user123",
    "topic": "Neural Networks",
    "duration_minutes": 30,
    "created_at": "2025-04-28T11:00:00.000Z",
    "activities": [...],
    "status": "in_progress",
    "current_activity_index": 1
  },
  {
    "session_id": "sess_d4e5f6",
    "user_id": "user123",
    "topic": "Deep Learning",
    "duration_minutes": 45,
    "created_at": "2025-04-27T14:00:00.000Z",
    "activities": [...],
    "status": "completed",
    "current_activity_index": 4
  }
]
```

**Error Responses**:
- `400 Bad Request`: User ID is required
- `500 Internal Server Error`: Error fetching user sessions

### Quiz Management

#### Generate Quiz

Generates a quiz with questions based on a specified topic.

- **URL**: `/quiz/generate`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  - `user_id`: String - User identifier
  - `topic`: String - Topic for the quiz
  - `num_questions`: Number - Number of questions to generate
  - `difficulty`: String - Difficulty level (e.g., "easy", "medium", "hard")
  - `save_quiz`: Boolean (optional) - Whether to save the quiz (default: true)

**Example Request**:
```bash
curl -X POST \
  http://localhost:5000/api/quiz/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user123",
    "topic": "Neural Networks",
    "num_questions": 5,
    "difficulty": "medium",
    "save_quiz": true
  }'
```

**Success Response (200 OK)**:
```json
{
  "id": "quiz_a1b2c3",
  "questions": [
    {
      "id": "q1",
      "text": "What is a neural network?",
      "options": {
        "A": "A computer network with high security",
        "B": "A mathematical model inspired by the human brain",
        "C": "A physical network of computers",
        "D": "A type of computer virus"
      },
      "correct_answer": "B",
      "explanation": "Neural networks are mathematical models inspired by the human brain's structure and function."
    },
    {
      "id": "q2",
      "text": "What is a neural network?",
      "options": {
        "A": "A computer network with high security",
        "B": "A mathematical model inspired by the human brain",
        "C": "A physical network of computers",
        "D": "A type of computer virus"
      },
      "correct_answer": "B",
      "explanation": "Neural networks are mathematical models inspired by the human brain's structure and function."
    }
    // Additional questions...
  ],
  "metadata": {
    "topic": "Neural Networks",
    "difficulty": "medium",
    "sources": ["machine_learning.pdf"]
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Error generating quiz

#### Get User Quizzes

Retrieves all quizzes for a given user.

- **URL**: `/quiz/user/:user_id`
- **Method**: `GET`
- **URL Parameters**:
  - `user_id`: String - User identifier

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/quiz/user/user123
```

**Success Response (200 OK)**:
```json
[
  {
    "id": "quiz_a1b2c3",
    "topic": "Neural Networks",
    "created_at": "2025-04-28T12:00:00.000Z",
    "questions": [...],
    "metadata": {
      "topic": "Neural Networks",
      "difficulty": "medium",
      "sources": ["machine_learning.pdf"]
    }
  },
  {
    "id": "quiz_d4e5f6",
    "topic": "Deep Learning",
    "created_at": "2025-04-27T15:00:00.000Z",
    "questions": [...],
    "metadata": {
      "topic": "Deep Learning",
      "difficulty": "hard",
      "sources": ["deep_learning.pdf"]
    }
  }
]
```

**Error Responses**:
- `400 Bad Request`: User ID is required
- `500 Internal Server Error`: Error fetching user quizzes

### Flashcard Management

#### Get Flashcards

Retrieves flashcards, optionally filtered by user.

- **URL**: `/flashcards`
- **Method**: `GET`
- **Query Parameters**:
  - `user_id`: String (optional) - User identifier to filter by

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/flashcards?user_id=user123
```

**Success Response (200 OK)**:
```json
[
  {
    "flashcard_id": "flashcard_set_a1b2c3",
    "user_id": "user123",
    "topic": "Neural Networks",
    "cards": [
      {
        "id": "card1",
        "front": "What is supervised learning?",
        "back": "Learning from labeled training data where the model is taught what correct outputs should look like."
      },
      {
        "id": "card2",
        "front": "What is unsupervised learning?",
        "back": "Learning from unlabeled data where the model finds patterns and relationships without explicit guidance."
      }
      // Additional cards...
    ],
    "metadata": {
      "topic": "Neural Networks",
      "card_count": 5,
      "sources": ["machine_learning.pdf"]
    },
    "created_at": "2025-04-28T13:00:00.000Z"
  }
]
```

**Error Response**:
- `500 Internal Server Error`: Error fetching flashcards

#### Generate Flashcards

Generates a set of flashcards based on a specified topic.

- **URL**: `/flashcard/generate`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  - `user_id`: String - User identifier
  - `topic`: String - Topic for the flashcards
  - `num_cards`: Number - Number of flashcards to generate
  - `save_flashcards`: Boolean (optional) - Whether to save the flashcards (default: true)

**Example Request**:
```bash
curl -X POST \
  http://localhost:5000/api/flashcard/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user123",
    "topic": "Neural Networks",
    "num_cards": 5,
    "save_flashcards": true
  }'
```

**Success Response (200 OK)**:
```json
{
  "id": "flashcard_set_a1b2c3",
  "cards": [
    {
      "id": "card1",
      "front": "What is supervised learning?",
      "back": "Learning from labeled training data where the model is taught what correct outputs should look like."
    },
    {
      "id": "card2",
      "front": "What is unsupervised learning?",
      "back": "Learning from unlabeled data where the model finds patterns and relationships without explicit guidance."
    }
    // Additional cards...
  ],
  "metadata": {
    "topic": "Neural Networks",
    "card_count": 5,
    "sources": ["machine_learning.pdf"]
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Error generating flashcards

### Chat

#### Send Chat Message

Sends a message to the AI assistant and receives a response.

- **URL**: `/chat/chat`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  - `user_id`: String - User identifier
  - `message`: String - User's message
  - `mode`: String - Chat mode ("tutor", "chat", "quiz", "flashcard")

**Example Request**:
```bash
curl -X POST \
  http://localhost:5000/api/chat/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user123",
    "message": "Explain how neural networks learn",
    "mode": "tutor"
  }'
```

**Success Response (200 OK)**:
```json
{
  "response": "Let's think about how neural networks learn. Can you tell me what you already know about how they process information?",
  "context_used": ["machine_learning.pdf", "neural_networks.md"]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Error generating chat response

## Data Models

### Session

```typescript
{
  id: number;
  session_id: string;
  user_id: string;
  topic: string;
  duration_minutes: number;
  created_at: string; // ISO date string
  activities: Activity[];
  status: string; // "planned", "in_progress", "completed"
  current_activity_index: number;
}
```

### Activity

```typescript
{
  type: 'introduction' | 'flashcard' | 'quiz' | 'summary';
  duration_minutes: number;
  description: string;
  parameters: {
    topic: string;
    [key: string]: any; // Additional parameters
  };
}
```

### Quiz

```typescript
{
  id: string;
  topic: string;
  created_at: string; // ISO date string
  questions: Question[];
  metadata: {
    topic: string;
    difficulty: string;
    sources: string[];
  };
}
```

### Question

```typescript
{
  id: string;
  text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  correct_answer: string;
  explanation: string;
}
```

### Flashcard Set

```typescript
{
  id: string;
  topic: string;
  created_at: string; // ISO date string
  cards: Card[];
  metadata: {
    topic: string;
    card_count: number;
    sources: string[];
  };
}
```

### Card

```typescript
{
  id: string;
  front: string;
  back: string;
}
```

## Implementation Notes

1. In a production environment, proper authentication and authorization should be implemented.
2. The current implementation uses mock data for AI-generated content. In a real-world scenario, this would connect to actual AI services.
3. File processing is simplified, with basic chunking logic. A production system would implement more sophisticated text processing and vector storage.
4. Error handling could be improved for better debugging and client feedback.
5. The API doesn't currently implement pagination, which would be necessary for large data sets.

## API Development

To extend the API:

1. Define new endpoint route handlers in `server/routes.ts`
2. Add appropriate storage methods in `server/storage.ts`
3. Define data models in `shared/schema.ts`
4. Add API client functions in `client/src/lib/api.ts`

---

This documentation provides a comprehensive reference for the AI-Powered Study Buddy API. For more detailed information about implementation, refer to the source code and associated comments.