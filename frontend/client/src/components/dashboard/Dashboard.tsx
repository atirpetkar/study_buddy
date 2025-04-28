import { useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import ProgressSummary from "./ProgressSummary";
import RecentActivity from "./RecentActivity";
import RecommendedTopics from "./RecommendedTopics";
import { 
  BookOpen, 
  Upload, 
  MessageCircle 
} from "lucide-react";

export default function Dashboard() {
  const [_, setLocation] = useLocation();
  
  // User ID would typically come from auth context
  const userId = "user123";
  
  const progressData = {
    studyTime: 4.5,
    studyTimePercentage: 65,
    quizzesCompleted: 12,
    quizzesPercentage: 75,
    flashcardsMastered: 42,
    flashcardsPercentage: 42
  };
  
  const recentActivities = [
    {
      type: "session",
      title: "Completed a Machine Learning study session",
      time: "Today, 10:30 AM",
      duration: "15 minutes",
      icon: "ri-time-line",
      iconBg: "bg-indigo-100",
      iconColor: "text-primary"
    },
    {
      type: "quiz",
      title: "Scored 85% on Neural Networks quiz",
      time: "Yesterday, 3:45 PM",
      detail: "5 questions",
      icon: "ri-question-line",
      iconBg: "bg-emerald-100",
      iconColor: "text-secondary"
    },
    {
      type: "flashcard",
      title: "Created Supervised Learning flashcards",
      time: "Apr 26, 2025",
      detail: "8 cards",
      icon: "ri-file-card-line",
      iconBg: "bg-amber-100",
      iconColor: "text-amber-500"
    }
  ];
  
  const recommendedTopics = [
    {
      title: "Deep Learning Fundamentals",
      source: "Based on your Machine Learning documents"
    },
    {
      title: "Neural Network Architectures",
      source: "Continue from your recent session"
    }
  ];
  
  const handleCreateQuickSession = () => {
    setLocation("/create-session");
  };
  
  const handleUploadDocuments = () => {
    setLocation("/documents");
  };
  
  const handleAskTutor = () => {
    setLocation("/chat");
  };
  
  return (
    <div className="px-4 py-6 md:px-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
      </div>
      
      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Button 
          className="bg-primary hover:bg-indigo-700 text-white py-6 h-auto"
          onClick={handleCreateQuickSession}
        >
          <BookOpen className="mr-2 h-5 w-5" /> Start Quick Session
        </Button>
        <Button 
          variant="outline" 
          className="bg-white hover:bg-gray-50 text-gray-800 py-6 h-auto"
          onClick={handleUploadDocuments}
        >
          <Upload className="mr-2 h-5 w-5" /> Upload Documents
        </Button>
        <Button 
          variant="outline" 
          className="bg-white hover:bg-gray-50 text-gray-800 py-6 h-auto"
          onClick={handleAskTutor}
        >
          <MessageCircle className="mr-2 h-5 w-5" /> Ask AI Tutor
        </Button>
      </div>
      
      {/* Progress Summary */}
      <ProgressSummary data={progressData} />
      
      {/* Recent Activity */}
      <RecentActivity activities={recentActivities} />
      
      {/* Recommended Topics */}
      <RecommendedTopics topics={recommendedTopics} />
    </div>
  );
}
