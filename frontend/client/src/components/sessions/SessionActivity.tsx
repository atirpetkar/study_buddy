import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, HelpCircle, FlipVertical, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { format } from "date-fns";

type Session = {
  session_id: string;
  user_id: string;
  topic: string;
  duration_minutes: number;
  created_at: string;
  status: string;
  activities: Array<{
    type: string;
    duration_minutes: number;
    description: string;
  }>;
  current_activity_index: number;
}

interface SessionActivityProps {
  session: Session;
  onClick: (sessionId: string) => void;
}

export default function SessionActivity({ session, onClick }: SessionActivityProps) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-200" variant="outline">Completed</Badge>;
      case 'in_progress':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200" variant="outline">In Progress</Badge>;
      case 'planned':
      default:
        return <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-200" variant="outline">Planned</Badge>;
    }
  };
  
  const getActivityIcons = (activities: any[] | undefined) => {
    if (!activities || !Array.isArray(activities) || activities.length === 0) {
      return <div className="flex space-x-1"></div>;
    }
    
    return (
      <div className="flex space-x-1">
        {activities.map((activity, i) => {
          let icon;
          switch (activity?.type) {
            case 'introduction':
              icon = <BookOpen className="h-4 w-4 text-indigo-500" />;
              break;
            case 'quiz':
              icon = <HelpCircle className="h-4 w-4 text-green-500" />;
              break;
            case 'flashcard':
              icon = <FlipVertical className="h-4 w-4 text-amber-500" />;
              break;
            case 'summary':
              icon = <FileText className="h-4 w-4 text-blue-500" />;
              break;
            default:
              icon = <FileText className="h-4 w-4 text-gray-500" />;
          }
          
          const currentIndex = session?.current_activity_index || 0;
          
          return (
            <div 
              key={i} 
              className={cn(
                "h-6 w-6 rounded-full flex items-center justify-center",
                i < currentIndex ? "bg-green-100" : 
                i === currentIndex ? "bg-blue-100" : 
                "bg-gray-100"
              )}
            >
              {icon}
            </div>
          );
        })}
      </div>
    );
  };
  
  const totalDuration = session.activities && Array.isArray(session.activities) 
    ? session.activities.reduce((sum, activity) => sum + (activity?.duration_minutes || 0), 0)
    : 0;
    
  const createdDate = session.created_at ? new Date(session.created_at) : new Date();
  const formattedDate = format(createdDate, 'MMM d, yyyy');
  const formattedTime = format(createdDate, 'h:mm a');
  
  return (
    <Card 
      className="mb-4 hover:shadow-md transition-shadow cursor-pointer" 
      onClick={() => onClick(session.session_id)}
    >
      <CardContent className="p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <h3 className="font-medium text-lg">{session.topic}</h3>
              {getStatusBadge(session.status)}
            </div>
            <p className="text-sm text-gray-600 mb-3">
              {formattedDate} at {formattedTime} · {totalDuration} min
            </p>
            <div className="flex items-center space-x-3">
              {getActivityIcons(session.activities)}
            </div>
          </div>
          <div className="mt-4 md:mt-0">
            <div className="text-primary hover:text-indigo-700">
              {session.status === 'completed' ? 'View Results' : 'Continue Session'}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
