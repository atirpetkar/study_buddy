import { useState } from "react";
import { FlipVertical, ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ActivityFlashcardProps {
  content: string;
}

type Flashcard = {
  front: string;
  back: string;
  confidence?: number; // 1-5 rating
};

export default function ActivityFlashcard({ content }: ActivityFlashcardProps) {
  // Parse the flashcard content
  const parseFlashcardContent = (content: string): Flashcard[] => {
    // In a real app, we'd parse actual flashcard content from the API
    // For now, create a sample flashcard from the content
    const parts = content.split("\n");
    const flashcards: Flashcard[] = [];
    
    if (content.includes("Flashcard")) {
      for (let i = 0; i < parts.length; i++) {
        if (parts[i].startsWith("Flashcard")) {
          const questionPart = parts[i].split(": ")[1];
          const answerPart = parts[i+1].replace("Answer: ", "");
          
          if (questionPart && answerPart) {
            flashcards.push({
              front: questionPart,
              back: answerPart,
            });
          }
        }
      }
    } else {
      // Fallback if no proper format is detected
      flashcards.push({
        front: "What is supervised learning?",
        back: "Learning from labeled training data where the model is taught what correct outputs should look like.",
      });
    }
    
    return flashcards;
  };
  
  const [flashcards, setFlashcards] = useState<Flashcard[]>(parseFlashcardContent(content));
  const [currentCard, setCurrentCard] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  
  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };
  
  const handlePrevious = () => {
    if (currentCard > 0) {
      setCurrentCard(currentCard - 1);
      setIsFlipped(false);
    }
  };
  
  const handleNext = () => {
    if (currentCard < flashcards.length - 1) {
      setCurrentCard(currentCard + 1);
      setIsFlipped(false);
    }
  };
  
  const handleConfidenceRating = (rating: number) => {
    const updatedFlashcards = [...flashcards];
    updatedFlashcards[currentCard].confidence = rating;
    setFlashcards(updatedFlashcards);
    
    // Automatically go to next card after rating
    if (currentCard < flashcards.length - 1) {
      setTimeout(() => {
        setCurrentCard(currentCard + 1);
        setIsFlipped(false);
      }, 500);
    }
  };
  
  return (
    <div className="activity-flashcard">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-500">
          <FlipVertical className="h-5 w-5" />
        </div>
        <h3 className="ml-3 text-lg font-medium text-gray-800">Review Key Concepts</h3>
      </div>
      
      <div 
        className={cn(
          "flashcard relative h-64 md:h-72 perspective-1000",
          "cursor-pointer"
        )}
        onClick={handleFlip}
      >
        <div 
          className={cn(
            "absolute w-full h-full transform transition-transform duration-500 ease-in-out",
            isFlipped ? "rotate-y-180" : ""
          )}
          style={{ 
            transformStyle: "preserve-3d",
            transform: isFlipped ? "rotateY(180deg)" : "" 
          }}
        >
          {/* Front of card */}
          <div 
            className={cn(
              "absolute w-full h-full bg-white border border-gray-200 rounded-xl p-8",
              "flex items-center justify-center backface-hidden"
            )}
            style={{ backfaceVisibility: "hidden" }}
          >
            <div className="text-center">
              <h4 className="text-xl font-medium text-gray-800">
                {flashcards[currentCard]?.front || "Loading..."}
              </h4>
              <p className="text-sm text-gray-500 mt-4">
                (Click to flip)
              </p>
            </div>
          </div>
          
          {/* Back of card */}
          <div 
            className={cn(
              "absolute w-full h-full bg-white border border-gray-200 rounded-xl p-8",
              "flex items-center justify-center backface-hidden overflow-auto"
            )}
            style={{ 
              backfaceVisibility: "hidden",
              transform: "rotateY(180deg)" 
            }}
          >
            <div className="text-center">
              <p className="text-gray-700">
                {flashcards[currentCard]?.back || "Loading..."}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-6 flex justify-center space-x-2">
        <Button 
          variant="outline" 
          onClick={handlePrevious}
          disabled={currentCard === 0}
        >
          <ArrowLeft className="mr-1 h-4 w-4" /> Previous
        </Button>
        
        <div className="flex">
          <Button
            className="py-2 px-3 rounded-l-md bg-red-100 hover:bg-red-200 text-red-700"
            variant="ghost"
            title="Didn't know"
            onClick={() => handleConfidenceRating(1)}
            disabled={!isFlipped}
          >
            1
          </Button>
          <Button
            className="py-2 px-3 bg-amber-100 hover:bg-amber-200 text-amber-700 rounded-none"
            variant="ghost"
            title="Hard to recall"
            onClick={() => handleConfidenceRating(2)}
            disabled={!isFlipped}
          >
            2
          </Button>
          <Button
            className="py-2 px-3 bg-yellow-100 hover:bg-yellow-200 text-yellow-700 rounded-none"
            variant="ghost"
            title="Recalled with effort"
            onClick={() => handleConfidenceRating(3)}
            disabled={!isFlipped}
          >
            3
          </Button>
          <Button
            className="py-2 px-3 bg-lime-100 hover:bg-lime-200 text-lime-700 rounded-none"
            variant="ghost"
            title="Recalled easily"
            onClick={() => handleConfidenceRating(4)}
            disabled={!isFlipped}
          >
            4
          </Button>
          <Button
            className="py-2 px-3 bg-green-100 hover:bg-green-200 text-green-700 rounded-r-md"
            variant="ghost"
            title="Perfect recall"
            onClick={() => handleConfidenceRating(5)}
            disabled={!isFlipped}
          >
            5
          </Button>
        </div>
        
        <Button 
          variant="outline" 
          onClick={handleNext}
          disabled={currentCard === flashcards.length - 1}
        >
          Next <ArrowRight className="ml-1 h-4 w-4" />
        </Button>
      </div>
      
      <div className="mt-4 flex justify-center">
        <span className="text-sm text-gray-500">
          Card {currentCard + 1} of {flashcards.length}
        </span>
      </div>
    </div>
  );
}
