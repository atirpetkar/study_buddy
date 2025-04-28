import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, HelpCircle } from "lucide-react";
import { generateQuiz } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

type Question = {
  id: string;
  text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  correct_answer: string;
  explanation: string;
  user_answer?: string;
  checked?: boolean;
};

type Quiz = {
  id: string;
  topic: string;
  created_at: string;
  questions: Question[];
  metadata: {
    topic: string;
    difficulty: string;
    sources: string[];
  };
};

export default function QuizzesPage() {
  const [activeTab, setActiveTab] = useState("create");
  const [topic, setTopic] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [quizComplete, setQuizComplete] = useState(false);
  
  const { toast } = useToast();

  // Fetch user's quizzes
  const { data: quizzes = [], isLoading } = useQuery({
    queryKey: ['/api/quiz/user', 'user123'], // Using placeholder user ID
    queryFn: async () => {
      try {
        const response = await fetch(`/api/quiz/user/user123`);
        if (!response.ok) throw new Error('Failed to fetch quizzes');
        return response.json();
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        return [];
      }
    }
  });

  // Generate a new quiz
  const generateQuizMutation = useMutation({
    mutationFn: generateQuiz,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['/api/quiz/user', 'user123'] });
      startQuiz(data);
      toast({
        title: "Quiz generated",
        description: `Created a new quiz on ${topic}`,
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to generate quiz. Please try again.",
        variant: "destructive",
      });
    }
  });

  const handleCreateQuiz = () => {
    if (!topic) {
      toast({
        title: "Error",
        description: "Please enter a topic",
        variant: "destructive",
      });
      return;
    }

    generateQuizMutation.mutate({
      user_id: "user123", // Using placeholder user ID
      topic,
      num_questions: numQuestions,
      difficulty,
      save_quiz: true
    });
  };

  const startQuiz = (quiz: Quiz) => {
    setActiveQuiz(quiz);
    setCurrentQuestionIndex(0);
    setQuizComplete(false);
    setActiveTab("take");
  };

  const handleAnswerSelect = (questionId: string, answer: string) => {
    if (!activeQuiz) return;
    
    const updatedQuestions = activeQuiz.questions.map(q => 
      q.id === questionId 
        ? { ...q, user_answer: answer } 
        : q
    );
    
    setActiveQuiz({
      ...activeQuiz,
      questions: updatedQuestions
    });
  };

  const handleCheckAnswer = () => {
    if (!activeQuiz) return;
    
    const currentQuestion = activeQuiz.questions[currentQuestionIndex];
    if (!currentQuestion.user_answer) {
      toast({
        title: "Select an answer",
        description: "Please select an answer before checking.",
        variant: "destructive",
      });
      return;
    }
    
    const updatedQuestions = [...activeQuiz.questions];
    updatedQuestions[currentQuestionIndex] = {
      ...currentQuestion,
      checked: true
    };
    
    setActiveQuiz({
      ...activeQuiz,
      questions: updatedQuestions
    });
  };

  const handleNextQuestion = () => {
    if (!activeQuiz) return;
    
    if (currentQuestionIndex < activeQuiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      setQuizComplete(true);
    }
  };

  const calculateScore = () => {
    if (!activeQuiz) return { correct: 0, total: 0 };
    
    const correct = activeQuiz.questions.filter(
      q => q.user_answer === q.correct_answer
    ).length;
    
    return {
      correct,
      total: activeQuiz.questions.length,
      percentage: Math.round((correct / activeQuiz.questions.length) * 100)
    };
  };

  const resetQuiz = () => {
    setActiveQuiz(null);
    setCurrentQuestionIndex(0);
    setQuizComplete(false);
    setActiveTab("history");
  };

  return (
    <div className="container max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Quizzes</h1>
      
      <Tabs defaultValue="create" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="create">Create Quiz</TabsTrigger>
          <TabsTrigger value="history">Quiz History</TabsTrigger>
          {activeQuiz && <TabsTrigger value="take">Take Quiz</TabsTrigger>}
        </TabsList>
        
        <TabsContent value="create">
          <Card>
            <CardHeader>
              <CardTitle>Create a New Quiz</CardTitle>
              <CardDescription>
                Generate a quiz on any topic to test your knowledge
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="topic">Topic</Label>
                <Input
                  id="topic"
                  placeholder="e.g. Neural Networks, World War II, Shakespeare..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="questions">Number of Questions</Label>
                  <Select
                    value={numQuestions.toString()}
                    onValueChange={(val) => setNumQuestions(parseInt(val))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Number of questions" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3">3 Questions</SelectItem>
                      <SelectItem value="5">5 Questions</SelectItem>
                      <SelectItem value="10">10 Questions</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="difficulty">Difficulty</Label>
                  <Select
                    value={difficulty}
                    onValueChange={setDifficulty}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Difficulty level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <Button 
                onClick={handleCreateQuiz} 
                className="w-full" 
                disabled={generateQuizMutation.isPending}
              >
                {generateQuizMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Quiz
                  </>
                ) : (
                  "Generate Quiz"
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Quiz History</CardTitle>
              <CardDescription>
                Review your past quizzes and results
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : quizzes.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <HelpCircle className="mx-auto h-12 w-12 opacity-30 mb-2" />
                  <p>You haven't taken any quizzes yet.</p>
                  <Button 
                    variant="outline" 
                    className="mt-4"
                    onClick={() => setActiveTab("create")}
                  >
                    Create Your First Quiz
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {quizzes.map((quiz: Quiz) => (
                    <Card key={quiz.id} className="overflow-hidden">
                      <div className="border-l-4 border-primary">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-center">
                            <div>
                              <h3 className="font-medium text-gray-800">
                                {quiz.metadata.topic}
                              </h3>
                              <p className="text-sm text-gray-500">
                                {new Date(quiz.created_at).toLocaleDateString()} • 
                                {quiz.questions.length} questions • 
                                {quiz.metadata.difficulty} difficulty
                              </p>
                            </div>
                            <Button onClick={() => startQuiz(quiz)}>
                              Take Quiz
                            </Button>
                          </div>
                        </CardContent>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="take">
          {activeQuiz && (
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>{activeQuiz.metadata.topic}</CardTitle>
                  <div className="text-sm text-gray-500">
                    Question {currentQuestionIndex + 1} of {activeQuiz.questions.length}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {quizComplete ? (
                  <div className="text-center py-8">
                    <h3 className="text-2xl font-bold mb-2">Quiz Complete!</h3>
                    <div className="text-4xl font-bold text-primary my-4">
                      {calculateScore().correct}/{calculateScore().total} Correct
                    </div>
                    <p className="text-xl mb-4">
                      You scored {calculateScore().percentage}%
                    </p>
                    <div className="flex gap-4 justify-center mt-6">
                      <Button variant="outline" onClick={resetQuiz}>
                        Back to History
                      </Button>
                      <Button onClick={() => {
                        setCurrentQuestionIndex(0);
                        setQuizComplete(false);
                      }}>
                        Review Answers
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="mb-6">
                      <h3 className="text-xl font-medium mb-4">
                        {activeQuiz.questions[currentQuestionIndex].text}
                      </h3>
                      
                      <div className="space-y-3">
                        {Object.entries(activeQuiz.questions[currentQuestionIndex].options).map(([key, value]) => (
                          <div 
                            key={key}
                            className={`
                              p-3 border rounded-md cursor-pointer
                              ${activeQuiz.questions[currentQuestionIndex].user_answer === key ? 'border-primary bg-primary/5' : 'border-gray-200 hover:border-gray-300'}
                              ${activeQuiz.questions[currentQuestionIndex].checked && key === activeQuiz.questions[currentQuestionIndex].correct_answer ? 'border-green-500 bg-green-50' : ''}
                              ${activeQuiz.questions[currentQuestionIndex].checked && activeQuiz.questions[currentQuestionIndex].user_answer === key && key !== activeQuiz.questions[currentQuestionIndex].correct_answer ? 'border-red-500 bg-red-50' : ''}
                            `}
                            onClick={() => {
                              if (!activeQuiz.questions[currentQuestionIndex].checked) {
                                handleAnswerSelect(activeQuiz.questions[currentQuestionIndex].id, key);
                              }
                            }}
                          >
                            <div className="flex items-center">
                              <div className={`
                                w-6 h-6 rounded-full flex items-center justify-center mr-3
                                ${activeQuiz.questions[currentQuestionIndex].user_answer === key ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700'}
                                ${activeQuiz.questions[currentQuestionIndex].checked && key === activeQuiz.questions[currentQuestionIndex].correct_answer ? 'bg-green-500 text-white' : ''}
                                ${activeQuiz.questions[currentQuestionIndex].checked && activeQuiz.questions[currentQuestionIndex].user_answer === key && key !== activeQuiz.questions[currentQuestionIndex].correct_answer ? 'bg-red-500 text-white' : ''}
                              `}>
                                {key}
                              </div>
                              <span>{value}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {activeQuiz.questions[currentQuestionIndex].checked && (
                      <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-md">
                        <h4 className="font-medium mb-2">Explanation</h4>
                        <p>{activeQuiz.questions[currentQuestionIndex].explanation}</p>
                      </div>
                    )}
                    
                    <div className="flex justify-between">
                      {!activeQuiz.questions[currentQuestionIndex].checked ? (
                        <Button onClick={handleCheckAnswer} disabled={!activeQuiz.questions[currentQuestionIndex].user_answer}>
                          Check Answer
                        </Button>
                      ) : (
                        <Button onClick={handleNextQuestion}>
                          {currentQuestionIndex < activeQuiz.questions.length - 1 ? "Next Question" : "Finish Quiz"}
                        </Button>
                      )}
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}