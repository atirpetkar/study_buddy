import { users, documents, sessions, quizzes, flashcards } from "@shared/schema";
import type { User, InsertUser, Document, InsertDocument, Session, InsertSession, Quiz, InsertQuiz, Flashcard, InsertFlashcard } from "@shared/schema";

// modify the interface with any CRUD methods
// you might need

export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Document methods
  createDocument(document: InsertDocument): Promise<Document>;
  getDocument(id: number): Promise<Document | undefined>;
  getAllDocuments(): Promise<Document[]>;
  
  // Session methods
  createSession(session: InsertSession): Promise<Session>;
  getSessionById(sessionId: string): Promise<Session | undefined>;
  getSessionsByUserId(userId: string): Promise<Session[]>;
  updateSessionStatus(sessionId: string, status: string, currentActivityIndex: number): Promise<void>;
  
  // Quiz methods
  createQuiz(quiz: InsertQuiz): Promise<Quiz>;
  getQuizById(quizId: string): Promise<Quiz | undefined>;
  getQuizzesByUserId(userId: string): Promise<Quiz[]>;
  
  // Flashcard methods
  createFlashcard(flashcard: InsertFlashcard): Promise<Flashcard>;
  getFlashcardById(flashcardId: string): Promise<Flashcard | undefined>;
  getFlashcardsByUserId(userId: string): Promise<Flashcard[]>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private documents: Map<number, Document>;
  private sessionsBySessionId: Map<string, Session>;
  private quizzesByQuizId: Map<string, Quiz>;
  private flashcardsByFlashcardId: Map<string, Flashcard>;
  
  private userId: number;
  private documentId: number;
  private sessionId: number;
  private quizId: number;
  private flashcardId: number;

  constructor() {
    this.users = new Map();
    this.documents = new Map();
    this.sessionsBySessionId = new Map();
    this.quizzesByQuizId = new Map();
    this.flashcardsByFlashcardId = new Map();
    
    this.userId = 1;
    this.documentId = 1;
    this.sessionId = 1;
    this.quizId = 1;
    this.flashcardId = 1;
    
    // Add a default user
    this.createUser({ username: "testuser", password: "password" });
  }

  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.userId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }
  
  // Document methods
  async createDocument(insertDocument: InsertDocument): Promise<Document> {
    const id = this.documentId++;
    const document: Document = { 
      ...insertDocument, 
      id, 
      upload_time: new Date() 
    };
    this.documents.set(id, document);
    return document;
  }
  
  async getDocument(id: number): Promise<Document | undefined> {
    return this.documents.get(id);
  }
  
  async getAllDocuments(): Promise<Document[]> {
    return Array.from(this.documents.values());
  }
  
  // Session methods
  async createSession(insertSession: InsertSession): Promise<Session> {
    const id = this.sessionId++;
    const session: Session = {
      ...insertSession,
      id,
      created_at: new Date(),
      current_activity_index: 0
    };
    this.sessionsBySessionId.set(insertSession.session_id, session);
    return session;
  }
  
  async getSessionById(sessionId: string): Promise<Session | undefined> {
    return this.sessionsBySessionId.get(sessionId);
  }
  
  async getSessionsByUserId(userId: string): Promise<Session[]> {
    return Array.from(this.sessionsBySessionId.values())
      .filter(session => session.user_id === userId);
  }
  
  async updateSessionStatus(sessionId: string, status: string, currentActivityIndex: number): Promise<void> {
    const session = this.sessionsBySessionId.get(sessionId);
    if (session) {
      session.status = status;
      session.current_activity_index = currentActivityIndex;
      this.sessionsBySessionId.set(sessionId, session);
    }
  }
  
  // Quiz methods
  async createQuiz(insertQuiz: InsertQuiz): Promise<Quiz> {
    const id = this.quizId++;
    const quiz: Quiz = {
      ...insertQuiz,
      id,
      created_at: new Date()
    };
    this.quizzesByQuizId.set(insertQuiz.quiz_id, quiz);
    return quiz;
  }
  
  async getQuizById(quizId: string): Promise<Quiz | undefined> {
    return this.quizzesByQuizId.get(quizId);
  }
  
  async getQuizzesByUserId(userId: string): Promise<Quiz[]> {
    return Array.from(this.quizzesByQuizId.values())
      .filter(quiz => quiz.user_id === userId);
  }
  
  // Flashcard methods
  async createFlashcard(insertFlashcard: InsertFlashcard): Promise<Flashcard> {
    const id = this.flashcardId++;
    const flashcard: Flashcard = {
      ...insertFlashcard,
      id,
      created_at: new Date()
    };
    this.flashcardsByFlashcardId.set(insertFlashcard.flashcard_id, flashcard);
    return flashcard;
  }
  
  async getFlashcardById(flashcardId: string): Promise<Flashcard | undefined> {
    return this.flashcardsByFlashcardId.get(flashcardId);
  }
  
  async getFlashcardsByUserId(userId: string): Promise<Flashcard[]> {
    return Array.from(this.flashcardsByFlashcardId.values())
      .filter(flashcard => flashcard.user_id === userId);
  }
}

export const storage = new MemStorage();
