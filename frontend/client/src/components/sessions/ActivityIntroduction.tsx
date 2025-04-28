import { BookOpen } from "lucide-react";

interface ActivityIntroductionProps {
  content: string;
}

export default function ActivityIntroduction({ content }: ActivityIntroductionProps) {
  return (
    <div className="activity-introduction">
      <div className="flex items-center mb-4">
        <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-primary">
          <BookOpen className="h-5 w-5" />
        </div>
        <h3 className="ml-3 text-lg font-medium text-gray-800">Introduction</h3>
      </div>
      <div className="prose max-w-none">
        {content.split('\n').map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>
    </div>
  );
}
