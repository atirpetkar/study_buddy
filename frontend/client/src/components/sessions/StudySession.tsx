import { useState, useEffect } from "react";
import { useLocation, useParams } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ChevronLeft, ChevronRight, Timer, MoreHorizontal } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { executeActivity } from "@/lib/api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import ActivityIntroduction from "./ActivityIntroduction";
import ActivityQuiz from "./ActivityQuiz";
import ActivityFlashcard from "./ActivityFlashcard";
import ActivitySummary from "./ActivitySummary";
import { useToast } from "@/hooks/use-toast";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export default function StudySession() {
  const { id } = useParams();
  const [_, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [confirmExit, setConfirmExit] = useState(false);
  const [remainingTime, setRemainingTime] = useState("15:00");
  
  const { data: session, isLoading, error } = useQuery({
    queryKey: ['/api/session/user', 'user123'],
    queryFn: async () => {
      // Simulate fetching the specific session - in a real app, you'd have a getSessionById API call
      const sessions = await fetch('/api/session/user/user123').then(res => res.json());
      const session = sessions.find((s: any) => s.session_id === id);
      if (!session) throw new Error("Session not found");
      return session;
    },
  });
  
  const executeMutation = useMutation({
    mutationFn: executeActivity,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['/api/session/user', 'user123'] });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to execute activity. Please try again.",
        variant: "destructive",
      });
    },
  });
  
  const [currentActivityData, setCurrentActivityData] = useState<any>(null);
  
  // Execute current activity when session loads or activity changes
  useEffect(() => {
    if (session && !currentActivityData) {
      executeCurrentActivity();
    }
  }, [session]);
  
  const executeCurrentActivity = () => {
    if (!session) return;
    
    executeMutation.mutate({
      session_id: session.session_id,
      activity_index: session.current_activity_index
    });
  };
  
  useEffect(() => {
    if (executeMutation.data) {
      setCurrentActivityData(executeMutation.data);
    }
  }, [executeMutation.data]);
  
  const handlePreviousActivity = () => {
    if (!session || session.current_activity_index <= 0) return;
    
    const prevIndex = session.current_activity_index - 1;
    executeMutation.mutate({
      session_id: session.session_id,
      activity_index: prevIndex
    });
  };
  
  const handleNextActivity = () => {
    if (!session || !currentActivityData) return;
    
    if (!session.activities || currentActivityData.next_activity_index >= (session.activities?.length || 0)) {
      // End of session
      toast({
        title: "Session Complete",
        description: "You've completed all activities in this session!",
      });
      return;
    }
    
    executeMutation.mutate({
      session_id: session.session_id,
      activity_index: currentActivityData.next_activity_index
    });
  };
  
  const handleCloseSession = () => {
    if (session?.status === 'in_progress') {
      setConfirmExit(true);
    } else {
      setLocation('/sessions');
    }
  };
  
  const renderActivityContent = () => {
    if (!currentActivityData) return null;
    
    const { activity, result } = currentActivityData;
    
    switch (activity.type) {
      case 'introduction':
        return <ActivityIntroduction content={result} />;
      case 'quiz':
        return <ActivityQuiz content={result} />;
      case 'flashcard':
        return <ActivityFlashcard content={result} />;
      case 'summary':
        return <ActivitySummary content={result} />;
      default:
        return <div className="p-4">Unsupported activity type</div>;
    }
  };
  
  if (isLoading) {
    return (
      <div className="px-4 py-6 md:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Loading Study Session...</h1>
        </div>
        
        <Card className="mb-8 animate-pulse">
          <CardContent className="p-6">
            <div className="h-8 bg-gray-200 rounded mb-4 w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded mb-8 w-1/2"></div>
            <div className="flex justify-end">
              <div className="h-4 bg-gray-200 rounded w-32"></div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="mb-8 h-64 animate-pulse">
          <CardContent className="p-6">
            <div className="h-8 bg-gray-200 rounded mb-4 w-1/3"></div>
            <div className="h-4 bg-gray-200 rounded mb-2 w-full"></div>
            <div className="h-4 bg-gray-200 rounded mb-2 w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  if (error || !session) {
    return (
      <div className="px-4 py-6 md:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Error Loading Session</h1>
        </div>
        
        <Card className="mb-8">
          <CardContent className="p-6 text-center">
            <p className="text-red-500 mb-4">Failed to load the study session.</p>
            <Button onClick={() => setLocation('/sessions')}>
              Return to Sessions
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  const progressPercentage = session.activities && session.activities.length > 0 
    ? (session.current_activity_index / session.activities.length) * 100
    : 0;
  
  return (
    <div className="px-4 py-6 md:px-8">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <Button variant="ghost" size="icon" onClick={handleCloseSession} className="mr-2">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-2xl font-bold text-gray-800">Study Session</h1>
        </div>
        <div className="flex items-center space-x-3">
          <div className="bg-indigo-100 text-primary py-1 px-3 rounded-full text-sm font-medium flex items-center">
            <Timer className="h-4 w-4 mr-1" />
            <span>{remainingTime}</span>
          </div>
          <Button variant="ghost" size="icon">
            <MoreHorizontal className="h-5 w-5" />
          </Button>
        </div>
      </div>
      
      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-800">{session.topic}</h2>
              <p className="text-gray-600 mt-1">
                A {session.duration_minutes}-minute session on key concepts
              </p>
            </div>
            <div className="mt-4 md:mt-0">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Progress:</span>
                <div className="flex items-center">
                  <span className="text-sm font-medium text-primary">
                    {session.current_activity_index !== undefined ? session.current_activity_index + 1 : 0}
                  </span>
                  <span className="text-sm text-gray-600">/</span>
                  <span className="text-sm text-gray-600">
                    {session.activities && session.activities.length ? session.activities.length : 0}
                  </span>
                </div>
              </div>
              <Progress className="w-full h-2 mt-2" value={progressPercentage} />
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card className="mb-8">
        <CardContent className="p-6">
          {executeMutation.isPending ? (
            <div className="py-20 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading activity...</p>
            </div>
          ) : (
            renderActivityContent()
          )}
        </CardContent>
      </Card>
      
      <div className="flex justify-between items-center">
        <Button 
          variant="outline" 
          onClick={handlePreviousActivity}
          disabled={
            session.current_activity_index === undefined || 
            session.current_activity_index <= 0 || 
            executeMutation.isPending
          }
        >
          <ChevronLeft className="mr-1 h-4 w-4" /> Previous
        </Button>
        <Button 
          onClick={handleNextActivity}
          disabled={
            !currentActivityData || 
            !session.activities ||
            currentActivityData.next_activity_index >= (session.activities?.length || 0) || 
            executeMutation.isPending
          }
        >
          Next <ChevronRight className="ml-1 h-4 w-4" />
        </Button>
      </div>
      
      <AlertDialog open={confirmExit} onOpenChange={setConfirmExit}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Exit Study Session?</AlertDialogTitle>
            <AlertDialogDescription>
              Your session is still in progress. Are you sure you want to exit? Your progress will be saved.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => setLocation('/sessions')}>
              Exit Session
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
