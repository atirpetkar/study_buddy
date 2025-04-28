import { useState } from "react";
import { useLocation } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Plus } from "lucide-react";
import SessionActivity from "@/components/sessions/SessionActivity";
import { getUserSessions } from "@/lib/api";

export default function SessionsPage() {
  const [_, setLocation] = useLocation();
  const userId = "user123"; // In a real app, this would come from auth
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['/api/session/user', userId],
    queryFn: async () => {
      try {
        const sessions = await getUserSessions(userId);
        // Ensure we always return an array, even if the API returns something else
        return Array.isArray(sessions) ? sessions : [];
      } catch (error) {
        console.error("Error fetching sessions:", error);
        return [];
      }
    },
  });
  
  const handleCreateSession = () => {
    setLocation("/create-session");
  };
  
  const handleSessionClick = (sessionId: string) => {
    setLocation(`/session/${sessionId}`);
  };
  
  return (
    <div className="px-4 py-6 md:px-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Study Sessions</h1>
        <Button onClick={handleCreateSession}>
          <Plus className="h-4 w-4 mr-2" /> New Session
        </Button>
      </div>
      
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-5">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : error ? (
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-red-500 mb-4">Failed to load sessions</p>
            <Button 
              variant="outline" 
              onClick={() => window.location.reload()}
              className="mx-auto"
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      ) : !data || data.length === 0 ? (
        <Card>
          <CardContent className="p-10 text-center">
            <h3 className="text-lg font-medium text-gray-800 mb-2">No Study Sessions Yet</h3>
            <p className="text-gray-600 mb-6">Create your first study session to start learning</p>
            <Button onClick={handleCreateSession}>
              <Plus className="h-4 w-4 mr-2" /> Create Study Session
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {data.map((session: any, index: number) => (
            <SessionActivity
              key={index}
              session={session}
              onClick={handleSessionClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}
