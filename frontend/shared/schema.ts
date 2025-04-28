import { pgTable, text, serial, integer, boolean, timestamp, json } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const documents = pgTable("documents", {
  id: serial("id").primaryKey(),
  filename: text("filename").notNull(),
  filetype: text("filetype").notNull(),
  upload_time: timestamp("upload_time").defaultNow().notNull(),
  chunk_count: integer("chunk_count").notNull(),
  user_id: integer("user_id").references(() => users.id),
});

export const sessions = pgTable("sessions", {
  id: serial("id").primaryKey(),
  session_id: text("session_id").notNull().unique(),
  user_id: text("user_id").notNull(),
  topic: text("topic").notNull(),
  duration_minutes: integer("duration_minutes").notNull(),
  created_at: timestamp("created_at").defaultNow().notNull(),
  activities: json("activities").notNull(),
  status: text("status").notNull(),
  current_activity_index: integer("current_activity_index").default(0),
});

export const quizzes = pgTable("quizzes", {
  id: serial("id").primaryKey(),
  quiz_id: text("quiz_id").notNull().unique(),
  user_id: text("user_id").notNull(),
  topic: text("topic").notNull(),
  questions: json("questions").notNull(),
  metadata: json("metadata").notNull(),
  created_at: timestamp("created_at").defaultNow().notNull(),
});

export const flashcards = pgTable("flashcards", {
  id: serial("id").primaryKey(),
  flashcard_id: text("flashcard_id").notNull().unique(),
  user_id: text("user_id").notNull(),
  topic: text("topic").notNull(),
  cards: json("cards").notNull(),
  metadata: json("metadata").notNull(),
  created_at: timestamp("created_at").defaultNow().notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertDocumentSchema = createInsertSchema(documents).pick({
  filename: true,
  filetype: true,
  chunk_count: true,
  user_id: true,
});

export const insertSessionSchema = createInsertSchema(sessions).pick({
  session_id: true,
  user_id: true,
  topic: true,
  duration_minutes: true,
  activities: true,
  status: true,
});

export const insertQuizSchema = createInsertSchema(quizzes).pick({
  quiz_id: true,
  user_id: true,
  topic: true,
  questions: true,
  metadata: true,
});

export const insertFlashcardSchema = createInsertSchema(flashcards).pick({
  flashcard_id: true,
  user_id: true,
  topic: true,
  cards: true,
  metadata: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export type InsertDocument = z.infer<typeof insertDocumentSchema>;
export type Document = typeof documents.$inferSelect;

export type InsertSession = z.infer<typeof insertSessionSchema>;
export type Session = typeof sessions.$inferSelect;

export type InsertQuiz = z.infer<typeof insertQuizSchema>;
export type Quiz = typeof quizzes.$inferSelect;

export type InsertFlashcard = z.infer<typeof insertFlashcardSchema>;
export type Flashcard = typeof flashcards.$inferSelect;

export type Activity = {
  type: 'introduction' | 'flashcard' | 'quiz' | 'summary';
  duration_minutes: number;
  description: string;
  parameters: Record<string, any>;
};
