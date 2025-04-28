import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLocation } from "wouter";
import { ArrowRight } from "lucide-react";

type Topic = {
  title: string;
  source: string;
};

interface RecommendedTopicsProps {
  topics: Topic[];
}

export default function RecommendedTopics({ topics }: RecommendedTopicsProps) {
  const [_, setLocation] = useLocation();
  
  const handleTopicClick = (topic: string) => {
    setLocation("/create-session");
    // Note: In wouter, we can't pass state directly with setLocation
    // We would need to use a state management solution to pass the topic
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommended Topics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topics.map((topic, index) => (
            <div 
              key={index} 
              className="border border-gray-200 rounded-lg p-4 hover:border-primary transition-colors duration-200 cursor-pointer"
              onClick={() => handleTopicClick(topic.title)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium text-gray-800">{topic.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{topic.source}</p>
                </div>
                <span className="text-primary">
                  <ArrowRight className="h-5 w-5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
