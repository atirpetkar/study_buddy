import { useState } from "react";
import { HelpCircle } from "lucide-react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ActivityQuizProps {
  content: string;
}

type Question = {
  text: string;
  options: { [key: string]: string };
  selected?: string;
  correct?: string;
  showFeedback?: boolean;
}

export default function ActivityQuiz({ content }: ActivityQuizProps) {
  // Parse the quiz content
  const parseQuizContent = (content: string) => {
    const questions: Question[] = [];
    const parts = content.split("\n\n");
    
    for (let i = 0; i < parts.length; i++) {
      if (parts[i].startsWith("Question")) {
        const questionText = parts[i].split("\n")[0].replace(/^Question \d+: /, "");
        const options: { [key: string]: string } = {};
        
        parts[i].split("\n").slice(1).forEach(line => {
          if (line.match(/^[A-D]\. /)) {
            const key = line.charAt(0);
            const value = line.substring(3);
            options[key] = value;
          }
        });
        
        questions.push({
          text: questionText,
          options,
          selected: undefined,
          correct: "B", // In a real app, this would come from the API
          showFeedback: false
        });
      }
    }
    
    return questions;
  };
  
  const [questions, setQuestions] = useState<Question[]>(parseQuizContent(content));
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [quizComplete, setQuizComplete] = useState(false);
  
  const handleOptionSelect = (value: string) => {
    const updatedQuestions = [...questions];
    updatedQuestions[currentQuestion].selected = value;
    setQuestions(updatedQuestions);
  };
  
  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Show all feedback when quiz is complete
      const updatedQuestions = questions.map(q => ({ ...q, showFeedback: true }));
      setQuestions(updatedQuestions);
      setQuizComplete(true);
    }
  };
  
  const handleCheckAnswer = () => {
    const updatedQuestions = [...questions];
    updatedQuestions[currentQuestion].showFeedback = true;
    setQuestions(updatedQuestions);
  };
  
  const getScore = () => {
    const correct = questions.filter(q => q.selected === q.correct).length;
    return `${correct}/${questions.length}`;
  };
  
  return (
    <div className="activity-quiz">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-secondary">
          <HelpCircle className="h-5 w-5" />
        </div>
        <h3 className="ml-3 text-lg font-medium text-gray-800">Test Your Knowledge</h3>
      </div>
      
      {quizComplete ? (
        <div className="text-center p-6">
          <h4 className="text-xl font-medium text-gray-800 mb-4">Quiz Complete</h4>
          <div className="text-3xl font-bold text-primary mb-6">{getScore()} correct</div>
          <div className="space-y-6">
            {questions.map((question, qIndex) => (
              <div key={qIndex} className="text-left border rounded-lg p-4">
                <h5 className="font-medium text-gray-800 mb-2">{question.text}</h5>
                {Object.entries(question.options).map(([key, value]) => (
                  <div 
                    key={key} 
                    className={cn(
                      "flex p-3 rounded-lg mb-2",
                      key === question.correct 
                        ? "bg-green-50 border border-green-200" 
                        : key === question.selected && key !== question.correct
                        ? "bg-red-50 border border-red-200"
                        : "bg-gray-50 border border-gray-200"
                    )}
                  >
                    <span className={cn(
                      "w-6 h-6 flex-shrink-0 rounded-full flex items-center justify-center mr-3",
                      key === question.correct
                        ? "bg-green-100 text-green-800 border border-green-300"
                        : key === question.selected && key !== question.correct
                        ? "bg-red-100 text-red-800 border border-red-300"
                        : "border border-gray-300 text-gray-600"
                    )}>{key}</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="mb-8">
          <h4 className="text-lg font-medium text-gray-800 mb-4">
            {questions[currentQuestion]?.text || "Loading question..."}
          </h4>
          
          <RadioGroup 
            value={questions[currentQuestion]?.selected} 
            onValueChange={handleOptionSelect}
            className="space-y-3"
          >
            {Object.entries(questions[currentQuestion]?.options || {}).map(([key, value]) => (
              <div 
                key={key} 
                className={cn(
                  "relative border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors",
                  questions[currentQuestion]?.selected === key && "border-primary bg-indigo-50",
                  questions[currentQuestion]?.showFeedback && key === questions[currentQuestion]?.correct && "border-green-500 bg-green-50",
                  questions[currentQuestion]?.showFeedback && questions[currentQuestion]?.selected === key && key !== questions[currentQuestion]?.correct && "border-red-500 bg-red-50"
                )}
              >
                <RadioGroupItem 
                  value={key} 
                  id={`option-${key}`} 
                  className="absolute left-4 top-1/2 -translate-y-1/2" 
                  disabled={questions[currentQuestion]?.showFeedback}
                />
                <Label 
                  htmlFor={`option-${key}`} 
                  className="flex py-1 pl-8 cursor-pointer"
                >
                  <span className={cn(
                    "w-6 h-6 flex-shrink-0 rounded-full flex items-center justify-center mr-3 border",
                    questions[currentQuestion]?.selected === key 
                      ? "border-primary bg-primary text-white" 
                      : "border-gray-300 text-gray-600"
                  )}>{key}</span>
                  <span>{value}</span>
                </Label>
              </div>
            ))}
          </RadioGroup>
          
          <div className="mt-6 flex justify-end">
            {questions[currentQuestion]?.showFeedback ? (
              <Button onClick={handleNextQuestion}>
                {currentQuestion < questions.length - 1 ? "Next Question" : "See Results"}
              </Button>
            ) : (
              <Button 
                onClick={handleCheckAnswer}
                disabled={!questions[currentQuestion]?.selected}
              >
                Check Answer
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
