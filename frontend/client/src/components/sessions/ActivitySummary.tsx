import { FileText } from "lucide-react";

interface ActivitySummaryProps {
  content: string;
}

export default function ActivitySummary({ content }: ActivitySummaryProps) {
  return (
    <div className="activity-summary">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-500">
          <FileText className="h-5 w-5" />
        </div>
        <h3 className="ml-3 text-lg font-medium text-gray-800">Session Summary</h3>
      </div>
      <div className="prose max-w-none">
        {content.split('\n').map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
        
        <p className="text-gray-700 mt-6">
          Take a moment to reflect on what you've learned. What concepts were most interesting 
          to you? Are there any areas you'd like to explore further in your next study session?
        </p>
      </div>
    </div>
  );
}
