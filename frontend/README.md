# AI-Powered Study Buddy Application Documentation

This documentation provides a comprehensive guide to the AI-powered Study Buddy application, designed to help GitHub Copilot understand the codebase and assist developers effectively.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Database Schema](#database-schema)
5. [Backend API](#backend-api)
6. [Frontend Components](#frontend-components)
7. [Setup and Running the Application](#setup-and-running-the-application)
8. [Development Guidelines](#development-guidelines)

## Project Overview

The AI-powered Study Buddy is an interactive learning application that processes study materials and creates personalized learning experiences through various activities like quizzes, flashcards, and guided study sessions. The application leverages AI to generate content, analyze user knowledge, and provide adaptive learning paths.

### Core Features

- **Document Management**: Upload and process study documents
- **Study Sessions**: Create adaptive learning sessions with various activities
- **Interactive Quizzes**: Test knowledge with AI-generated questions
- **Flashcards**: Review concepts with AI-created flashcards
- **AI Chat Assistant**: Get assistance and answers through chat
- **Progress Tracking**: Monitor study progress and achievements

## Technology Stack

### Frontend
- **React** (18.x) with TypeScript
- **Wouter** for routing
- **TanStack Query** (React Query) for data fetching
- **React Hook Form** with Zod validation
- **Tailwind CSS** for styling
- **shadcn/ui** components
- **Lucide React** for icons

### Backend
- **Node.js** with Express
- **TypeScript**
- **Drizzle ORM** with PostgreSQL
- **Zod** for schema validation
- **Multer** for file uploads

### Build Tools
- **Vite** for frontend development and bundling
- **ESBuild** for backend bundling
- **TSX** for TypeScript execution

## Project Structure

The application follows a modern full-stack JavaScript application structure with clear separation between frontend and backend code:

```
/
├── client/                # Frontend code
│   ├── src/
│   │   ├── assets/        # Static assets
│   │   ├── components/    # React components
│   │   │   ├── chat/      # Chat-related components
│   │   │   ├── dashboard/ # Dashboard components
│   │   │   ├── documents/ # Document management components
│   │   │   ├── layout/    # Layout components (Sidebar, MobileNav)
│   │   │   ├── sessions/  # Study session components
│   │   │   └── ui/        # UI components (shadcn/ui)
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility functions and API clients
│   │   ├── pages/         # Page components
│   │   ├── App.tsx        # Main application component
│   │   ├── index.css      # Global styles
│   │   └── main.tsx       # Application entry point
│   │
│   └── index.html         # HTML template
│
├── server/                # Backend code
│   ├── index.ts           # Server entry point
│   ├── routes.ts          # API route definitions
│   ├── storage.ts         # Storage interface and implementation
│   └── vite.ts            # Vite server setup for development
│
├── shared/                # Shared code between frontend and backend
│   └── schema.ts          # Database schema and type definitions
│
├── components.json        # shadcn/ui configuration
├── drizzle.config.ts      # Drizzle ORM configuration
├── package.json           # Project dependencies and scripts
├── postcss.config.js      # PostCSS configuration
├── tailwind.config.ts     # Tailwind CSS configuration
└── vite.config.ts         # Vite configuration
```

## Database Schema

The application uses Drizzle ORM with PostgreSQL. The database schema is defined in `shared/schema.ts` and includes the following tables:

### Users
- `id`: Serial primary key
- `username`: Text, not null, unique
- `password`: Text, not null

### Documents
- `id`: Serial primary key
- `filename`: Text, not null
- `filetype`: Text, not null
- `upload_time`: Timestamp, default now()
- `chunk_count`: Integer, not null
- `user_id`: Integer, references users.id

### Sessions
- `id`: Serial primary key
- `session_id`: Text, not null, unique
- `user_id`: Text, not null
- `topic`: Text, not null
- `duration_minutes`: Integer, not null
- `created_at`: Timestamp, default now()
- `activities`: JSON, not null
- `status`: Text, not null
- `current_activity_index`: Integer, default 0

### Quizzes
- `id`: Serial primary key
- `quiz_id`: Text, not null, unique
- `user_id`: Text, not null
- `topic`: Text, not null
- `questions`: JSON, not null
- `metadata`: JSON, not null
- `created_at`: Timestamp, default now()

### Flashcards
- `id`: Serial primary key
- `flashcard_id`: Text, not null, unique
- `user_id`: Text, not null
- `topic`: Text, not null
- `cards`: JSON, not null
- `metadata`: JSON, not null
- `created_at`: Timestamp, default now()

The schema also defines TypeScript types for each table, along with insert schemas using Drizzle-Zod for validation.

## Backend API

The backend API is implemented using Express and defined in `server/routes.ts`. Here are the main API endpoints:

### Document Management
- `POST /api/vectorstore/upload`: Upload documents
- `GET /api/vectorstore/documents`: Get all documents

### Study Sessions
- `POST /api/session/quick`: Create a quick study session
- `POST /api/session/execute`: Execute a session activity
- `GET /api/session/user/:user_id`: Get sessions for a user

### Quizzes
- `POST /api/quiz/generate`: Generate a quiz
- `GET /api/quiz/user/:user_id`: Get quizzes for a user

### Flashcards
- `GET /api/flashcards`: Get flashcards (optionally filtered by user)
- `POST /api/flashcard/generate`: Generate flashcards

### Chat
- `POST /api/chat/chat`: Send a message to the AI assistant

## Frontend Components

The frontend is built with React and organized into several key areas:

### Pages
- `DashboardPage`: Main dashboard with progress summary and recommendations
- `DocumentsPage`: Document management (upload, view, search)
- `SessionsPage`: View and manage study sessions
- `StudySessionPage`: Interactive study session interface
- `CreateSessionPage`: Create new study sessions
- `ChatPage`: Chat with the AI assistant
- `QuizzesPage`: Take and review quizzes
- `FlashcardsPage`: Study with flashcards

### Core Components
- `Sidebar` & `MobileNav`: Navigation components
- `ProgressSummary`: Shows study progress statistics
- `RecentActivity`: Displays recent learning activities
- `DocumentUpload` & `DocumentList`: Document management components
- `ChatInterface`: Interactive chat with the AI assistant
- `ActivityFlashcard`, `ActivityQuiz`, etc.: Various learning activity components

### UI Components
The application uses shadcn/ui components, which are based on Radix UI primitives. These components are located in `client/src/components/ui/` and include:
- Form controls (inputs, buttons, selects)
- Layout components (cards, accordions, tabs)
- Feedback components (toasts, alerts)
- And many more...

## Setup and Running the Application

### Prerequisites
- Node.js (v20.x recommended)
- PostgreSQL (v16.x)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd study-buddy
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up the database (if not using in-memory storage):
   ```bash
   npm run db:push
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5000`.

### Build for Production

```bash
npm run build
npm run start
```

## Development Guidelines

### Code Organization
- Backend logic should be minimal and focused on data persistence and API calls
- Frontend should handle most application logic
- Use shared types from `shared/schema.ts` for consistency
- Follow the storage interface in `server/storage.ts` for database interactions

### Frontend Development
- Use `wouter` for routing instead of directly manipulating the window
- Use `react-hook-form` with Zod validation for forms
- Use `@tanstack/react-query` for data fetching
- Always use the storage interface for CRUD operations
- Use Tailwind CSS for styling with shadcn/ui components

### API Development
- Validate request data using Zod schemas
- Keep routes thin, delegating business logic to appropriate services
- Handle errors consistently and provide meaningful error messages
- Follow REST principles for API design

### Type Safety
- Use TypeScript throughout the codebase
- Define types for API requests and responses
- Use Zod for runtime validation

### Styling
- Use Tailwind CSS for styling
- Follow the existing design system and color palette
- Use responsive design principles
- Use Lucide React for icons

---

This documentation provides a comprehensive overview of the AI-powered Study Buddy application. For more detailed information about specific components or features, please refer to the code comments and implementation details in the respective files.