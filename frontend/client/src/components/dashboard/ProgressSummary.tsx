import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

type ProgressData = {
  studyTime: number;
  studyTimePercentage: number;
  quizzesCompleted: number;
  quizzesPercentage: number;
  flashcardsMastered: number;
  flashcardsPercentage: number;
};

interface ProgressSummaryProps {
  data: ProgressData;
}

export default function ProgressSummary({ data }: ProgressSummaryProps) {
  return (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle>Your Learning Progress</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Study Time</span>
              <span className="text-sm font-medium text-primary">+15% this week</span>
            </div>
            <div className="flex items-end space-x-2">
              <span className="text-2xl font-bold text-gray-800">{data.studyTime}</span>
              <span className="text-gray-600">hours</span>
            </div>
            <div className="mt-2">
              <Progress value={data.studyTimePercentage} className="h-2 bg-gray-200" />
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Quizzes Completed</span>
              <span className="text-sm font-medium text-secondary">+3 this week</span>
            </div>
            <div className="flex items-end space-x-2">
              <span className="text-2xl font-bold text-gray-800">{data.quizzesCompleted}</span>
              <span className="text-gray-600">quizzes</span>
            </div>
            <div className="mt-2">
              <Progress value={data.quizzesPercentage} className="h-2 bg-gray-200" />
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Flashcards Mastered</span>
              <span className="text-sm font-medium text-amber-500">+8 this week</span>
            </div>
            <div className="flex items-end space-x-2">
              <span className="text-2xl font-bold text-gray-800">{data.flashcardsMastered}</span>
              <span className="text-gray-600">cards</span>
            </div>
            <div className="mt-2">
              <Progress value={data.flashcardsPercentage} className="h-2 bg-gray-200" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
