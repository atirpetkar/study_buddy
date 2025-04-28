import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import express from "express";
import multer from "multer";
import path from "path";
import { z } from "zod";
import { nanoid } from "nanoid";

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
});

export async function registerRoutes(app: Express): Promise<Server> {
  // API Routes
  const apiRouter = express.Router();
  app.use("/api", apiRouter);

  // Document Management Routes
  apiRouter.post("/vectorstore/upload", upload.array("files"), async (req, res) => {
    try {
      if (!req.files || !Array.isArray(req.files) || req.files.length === 0) {
        return res.status(400).json({ message: "No files uploaded" });
      }

      const result = {
        status: "success",
        total_chunks: 0,
        files: [] as Array<{ file: string; chunks: number; metadatas: Array<{ chunk_index: number; length: number }> }>,
      };

      for (const file of req.files as Express.Multer.File[]) {
        const fileExtension = path.extname(file.originalname).substring(1);
        const chunks = Math.ceil(file.size / 1000); // Simplified: 1 chunk per 1000 bytes
        
        // In a real implementation, we would process the file for vector storage
        // For now, we'll mock the chunking metadata
        const metadatas = Array.from({ length: chunks }, (_, i) => ({
          chunk_index: i,
          length: Math.min(1000, file.size - i * 1000),
        }));
        
        await storage.createDocument({
          filename: file.originalname,
          filetype: fileExtension,
          chunk_count: chunks,
          user_id: 1, // Default user for now
        });

        result.total_chunks += chunks;
        result.files.push({
          file: file.originalname,
          chunks,
          metadatas,
        });
      }

      res.status(200).json(result);
    } catch (error) {
      console.error("Upload error:", error);
      res.status(500).json({ message: "Error uploading documents" });
    }
  });

  apiRouter.get("/vectorstore/documents", async (req, res) => {
    try {
      const documents = await storage.getAllDocuments();
      
      const result = {
        document_count: documents.length,
        total_chunks: documents.reduce((sum, doc) => sum + doc.chunk_count, 0),
        documents: documents.map(doc => ({
          filename: doc.filename,
          filetype: doc.filetype,
          upload_time: doc.upload_time,
          chunk_count: doc.chunk_count,
        })),
      };

      res.status(200).json(result);
    } catch (error) {
      console.error("Error fetching documents:", error);
      res.status(500).json({ message: "Error fetching documents" });
    }
  });

  // Study Session Routes
  apiRouter.post("/session/quick", async (req, res) => {
    try {
      const schema = z.object({
        user_id: z.string(),
        topic: z.string(),
        duration_minutes: z.number().int().positive(),
      });

      const validation = schema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid request data", errors: validation.error.format() });
      }

      const { user_id, topic, duration_minutes } = validation.data;
      
      // Create a balanced study session with activities
      const session_id = `sess_${nanoid(6)}`;
      const totalMinutes = duration_minutes;
      
      // Allocate time for each activity type
      const introTime = Math.max(2, Math.floor(totalMinutes * 0.2));
      const quizTime = Math.max(5, Math.floor(totalMinutes * 0.3));
      const flashcardTime = Math.max(5, Math.floor(totalMinutes * 0.3));
      const summaryTime = totalMinutes - introTime - quizTime - flashcardTime;
      
      const activities = [
        {
          type: "introduction",
          duration_minutes: introTime,
          description: `Introduction to ${topic}`,
          parameters: { topic }
        },
        {
          type: "flashcard",
          duration_minutes: flashcardTime,
          description: `Review key concepts in ${topic}`,
          parameters: { num_cards: 3, topic }
        },
        {
          type: "quiz",
          duration_minutes: quizTime,
          description: `Test your knowledge of ${topic}`,
          parameters: { num_questions: 2, difficulty: "medium", topic }
        },
        {
          type: "summary",
          duration_minutes: summaryTime,
          description: `Summarize what you've learned about ${topic}`,
          parameters: { topic }
        }
      ];

      const session = await storage.createSession({
        session_id,
        user_id,
        topic,
        duration_minutes,
        activities,
        status: "planned",
      });

      res.status(200).json({
        session_id,
        user_id,
        topic,
        duration_minutes,
        created_at: session.created_at,
        activities,
        status: "planned",
        current_activity_index: 0
      });
    } catch (error) {
      console.error("Error creating session:", error);
      res.status(500).json({ message: "Error creating study session" });
    }
  });

  apiRouter.post("/session/execute", async (req, res) => {
    try {
      const schema = z.object({
        session_id: z.string(),
        activity_index: z.number().int().nonnegative(),
      });

      const validation = schema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid request data", errors: validation.error.format() });
      }

      const { session_id, activity_index } = validation.data;
      
      const session = await storage.getSessionById(session_id);
      if (!session) {
        return res.status(404).json({ message: "Session not found" });
      }

      if (activity_index >= session.activities.length) {
        return res.status(400).json({ message: "Invalid activity index" });
      }

      const activity = session.activities[activity_index];
      let result = "";

      // Generate content based on activity type
      switch (activity.type) {
        case "introduction":
          result = `${activity.parameters.topic} is an important area of study that covers several key concepts...`;
          break;
        case "flashcard":
          result = "Flashcard 1: What is supervised learning?\nAnswer: Learning with labeled data.";
          break;
        case "quiz":
          result = "Question 1: What is supervised learning?\nA. Learning without labeled data\nB. Learning with labeled data\nC. Learning through trial and error\nD. Learning without a teacher\n\nQuestion 2: Which of these is NOT a type of machine learning?\nA. Supervised learning\nB. Unsupervised learning\nC. Reinforcement learning\nD. Reflective learning";
          break;
        case "summary":
          result = `In this session on ${activity.parameters.topic}, we covered several important concepts...`;
          break;
      }

      // Update session status
      const next_activity_index = activity_index + 1 < session.activities.length ? activity_index + 1 : activity_index;
      const status = next_activity_index === activity_index && activity_index === session.activities.length - 1 ? "completed" : "in_progress";
      
      await storage.updateSessionStatus(session_id, status, next_activity_index);

      res.status(200).json({
        session_id,
        activity,
        result,
        next_activity_index,
        status
      });
    } catch (error) {
      console.error("Error executing activity:", error);
      res.status(500).json({ message: "Error executing activity" });
    }
  });

  apiRouter.get("/session/user/:user_id", async (req, res) => {
    try {
      const user_id = req.params.user_id;
      if (!user_id) {
        return res.status(400).json({ message: "User ID is required" });
      }

      const sessions = await storage.getSessionsByUserId(user_id);
      res.status(200).json(sessions);
    } catch (error) {
      console.error("Error fetching sessions:", error);
      res.status(500).json({ message: "Error fetching user sessions" });
    }
  });

  // Quiz Routes
  apiRouter.post("/quiz/generate", async (req, res) => {
    try {
      const schema = z.object({
        user_id: z.string(),
        topic: z.string(),
        num_questions: z.number().int().positive(),
        difficulty: z.string(),
        save_quiz: z.boolean().optional(),
      });

      const validation = schema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid request data", errors: validation.error.format() });
      }

      const { user_id, topic, num_questions, difficulty, save_quiz = true } = validation.data;
      
      // Generate a quiz (in a real app, this would use AI to generate content)
      const quiz_id = `quiz_${nanoid(6)}`;
      
      const questions = Array.from({ length: num_questions }, (_, i) => ({
        id: `q${i+1}`,
        text: `What is a neural network?`,
        options: {
          A: "A computer network with high security",
          B: "A mathematical model inspired by the human brain",
          C: "A physical network of computers",
          D: "A type of computer virus"
        },
        correct_answer: "B",
        explanation: "Neural networks are mathematical models inspired by the human brain's structure and function."
      }));

      const metadata = {
        topic,
        difficulty,
        sources: ["machine_learning.pdf"]
      };

      // Optionally save the quiz
      if (save_quiz) {
        await storage.createQuiz({
          quiz_id,
          user_id,
          topic,
          questions,
          metadata
        });
      }

      res.status(200).json({
        id: quiz_id,
        questions,
        metadata
      });
    } catch (error) {
      console.error("Error generating quiz:", error);
      res.status(500).json({ message: "Error generating quiz" });
    }
  });
  
  apiRouter.get("/quiz/user/:user_id", async (req, res) => {
    try {
      const user_id = req.params.user_id;
      if (!user_id) {
        return res.status(400).json({ message: "User ID is required" });
      }

      const quizzes = await storage.getQuizzesByUserId(user_id);
      const formattedQuizzes = quizzes.map(quiz => ({
        id: quiz.quiz_id,
        topic: quiz.topic,
        created_at: quiz.created_at,
        questions: quiz.questions,
        metadata: quiz.metadata
      }));
      
      res.status(200).json(formattedQuizzes);
    } catch (error) {
      console.error("Error fetching quizzes:", error);
      res.status(500).json({ message: "Error fetching user quizzes" });
    }
  });

  // Flashcard Routes
  apiRouter.get("/flashcards", async (req, res) => {
    try {
      // Get all flashcards or filter by user if a user_id is provided
      const userId = req.query.user_id as string | undefined;
      
      let flashcards;
      if (userId) {
        flashcards = await storage.getFlashcardsByUserId(userId);
      } else {
        // In a real app with authentication, you'd typically only allow admins
        // to fetch all flashcards or restrict to user's own flashcards
        const allFlashcards = await storage.getFlashcardsByUserId("user_1"); // Default user for demo
        flashcards = allFlashcards;
      }
      
      // Ensure proper content type is set
      res.setHeader('Content-Type', 'application/json');
      res.status(200).json(flashcards);
    } catch (error) {
      console.error("Error fetching flashcards:", error);
      res.setHeader('Content-Type', 'application/json');
      res.status(500).json({ message: "Error fetching flashcards" });
    }
  });

  apiRouter.post("/flashcard/generate", async (req, res) => {
    try {
      const schema = z.object({
        user_id: z.string(),
        topic: z.string(),
        num_cards: z.number().int().positive(),
        save_flashcards: z.boolean().optional(),
      });

      const validation = schema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid request data", errors: validation.error.format() });
      }

      const { user_id, topic, num_cards, save_flashcards = true } = validation.data;
      
      // Generate flashcards (in a real app, this would use AI to generate content)
      const flashcard_id = `flashcard_set_${nanoid(6)}`;
      
      const cards = Array.from({ length: num_cards }, (_, i) => ({
        id: `card${i+1}`,
        front: "What is supervised learning?",
        back: "Learning from labeled training data where the model is taught what correct outputs should look like."
      }));

      const metadata = {
        topic,
        card_count: num_cards,
        sources: ["machine_learning.pdf"]
      };

      // Optionally save the flashcards
      if (save_flashcards) {
        await storage.createFlashcard({
          flashcard_id,
          user_id,
          topic,
          cards,
          metadata
        });
      }

      res.status(200).json({
        id: flashcard_id,
        cards,
        metadata
      });
    } catch (error) {
      console.error("Error generating flashcards:", error);
      res.status(500).json({ message: "Error generating flashcards" });
    }
  });

  // Chat Routes
  apiRouter.post("/chat/chat", async (req, res) => {
    try {
      const schema = z.object({
        user_id: z.string(),
        message: z.string(),
        mode: z.string(),
      });

      const validation = schema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid request data", errors: validation.error.format() });
      }

      const { user_id, message, mode } = validation.data;
      
      // Generate response based on mode
      let response;
      const context_used = ["machine_learning.pdf", "neural_networks.md"];
      
      switch (mode) {
        case "tutor":
          response = "Let's think about how neural networks learn. Can you tell me what you already know about how they process information?";
          break;
        case "chat":
          response = "Neural networks learn through a process called backpropagation, where they adjust their weights based on the error of their predictions.";
          break;
        case "quiz":
          response = "Here's a question about neural networks: What is backpropagation? A) A way to visualize networks B) A learning algorithm C) A network architecture D) A type of neural activation";
          break;
        case "flashcard":
          response = "I've created a flashcard for you. Front: What is backpropagation? Back: An algorithm used to train neural networks by calculating gradients of the loss function with respect to the weights.";
          break;
        default:
          response = "I'm not sure how to help with that mode. Try 'tutor', 'chat', 'quiz', or 'flashcard'.";
      }

      res.status(200).json({
        response,
        context_used
      });
    } catch (error) {
      console.error("Error generating chat response:", error);
      res.status(500).json({ message: "Error generating chat response" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
