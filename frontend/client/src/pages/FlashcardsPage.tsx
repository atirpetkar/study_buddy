import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiRequest } from "@/lib/queryClient";
import { ArrowRight, FlipVertical, Plus, Search } from "lucide-react";
import { cn } from "@/lib/utils";

type FlashcardSet = {
  id: string;
  topic: string;
  created_at: string;
  cards: {
    id: string;
    front: string;
    back: string;
  }[];
  metadata: {
    topic: string;
    card_count: number;
    sources: string[];
  };
};

type FlashcardDisplay = {
  front: string;
  back: string;
  confidence?: number; // 1-5 rating
};

export default function FlashcardsPage() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newFlashcardsTopic, setNewFlashcardsTopic] = useState("");
  const [numCards, setNumCards] = useState(5);
  const [activeSet, setActiveSet] = useState<FlashcardSet | null>(null);
  const [currentCard, setCurrentCard] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  // Query to get all flashcard sets
  const {
    data: flashcardSets,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["/api/flashcards"],
    queryFn: async ({ signal }) => {
      try {
        const response = await fetch("/api/flashcards?user_id=user_1", { // In a real app, get this from auth context
          method: "GET",
          signal,
          headers: {
            "Accept": "application/json",
          }
        });
        
        if (!response.ok) {
          throw new Error("Failed to fetch flashcards");
        }
        
        return response.json();
      } catch (err) {
        console.error("Error fetching flashcards:", err);
        // Return empty array if no flashcards found
        return [];
      }
    },
    initialData: [],
  });

  const filteredFlashcardSets = Array.isArray(flashcardSets)
    ? flashcardSets.filter((set: FlashcardSet) =>
        set?.topic?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  const handleCreateFlashcards = async () => {
    try {
      // Use fetch directly instead of apiRequest
      const response = await fetch("/api/flashcard/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user_id: "user_1", // In a real app, this would come from auth context
          topic: newFlashcardsTopic,
          num_cards: numCards,
          save_flashcards: true,
        })
      });

      if (response.ok) {
        toast({
          title: "Success!",
          description: "New flashcards created successfully.",
        });
        refetch();
        setIsCreateDialogOpen(false);
        setNewFlashcardsTopic("");
        setNumCards(5);
      } else {
        toast({
          title: "Error",
          description: "Failed to create flashcards. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleSelectFlashcardSet = (set: FlashcardSet) => {
    setActiveSet(set);
    setCurrentCard(0);
    setIsFlipped(false);
  };

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
    if (activeSet && currentCard < activeSet.cards.length - 1) {
      setCurrentCard(currentCard + 1);
      setIsFlipped(false);
    }
  };

  const handleConfidenceRating = (rating: number) => {
    // In a real app, you'd save this rating to the backend
    console.log(`Card ${currentCard} rated ${rating}/5`);
    
    // Automatically go to next card after rating
    if (activeSet && currentCard < activeSet.cards.length - 1) {
      setTimeout(() => {
        setCurrentCard(currentCard + 1);
        setIsFlipped(false);
      }, 500);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Flashcards</h1>
          <p className="text-gray-600 mt-1">
            Review and manage your flashcard sets
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" /> Create Flashcards
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Flashcards</DialogTitle>
                <DialogDescription>
                  Enter a topic to generate a new set of flashcards.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="topic">Topic</Label>
                  <Input
                    id="topic"
                    placeholder="e.g., Machine Learning Basics"
                    value={newFlashcardsTopic}
                    onChange={(e) => setNewFlashcardsTopic(e.target.value)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="numCards">Number of Cards</Label>
                  <Input
                    id="numCards"
                    type="number"
                    min={1}
                    max={20}
                    value={numCards}
                    onChange={(e) => setNumCards(parseInt(e.target.value))}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateFlashcards}>Generate</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <div className="lg:col-span-1">
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
              <Input
                placeholder="Search flashcards..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            {isLoading ? (
              <p>Loading flashcard sets...</p>
            ) : error ? (
              <p className="text-red-500">Error loading flashcards. Please try again.</p>
            ) : filteredFlashcardSets.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No flashcard sets found.</p>
                <p className="text-gray-500 mt-2">Create a new set to get started!</p>
              </div>
            ) : (
              filteredFlashcardSets.map((set: FlashcardSet) => (
                <Card
                  key={set.id}
                  className={cn(
                    "cursor-pointer hover:border-primary transition-colors",
                    activeSet?.id === set.id ? "border-primary" : ""
                  )}
                  onClick={() => handleSelectFlashcardSet(set)}
                >
                  <CardHeader className="py-4">
                    <CardTitle className="text-base">{set.topic}</CardTitle>
                    <CardDescription>
                      {set.metadata.card_count} cards
                    </CardDescription>
                  </CardHeader>
                </Card>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-3">
          {activeSet ? (
            <Card>
              <CardHeader>
                <CardTitle>{activeSet.topic}</CardTitle>
                <CardDescription>
                  {activeSet.metadata.card_count} cards | Created on{" "}
                  {new Date(activeSet.created_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div 
                  className={cn(
                    "flashcard relative h-64 md:h-80 perspective-1000",
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
                          {activeSet.cards[currentCard]?.front || "Loading..."}
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
                          {activeSet.cards[currentCard]?.back || "Loading..."}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6">
                  <p className="text-center text-gray-500 mb-4">
                    How well did you know this?
                  </p>
                  <div className="flex justify-center space-x-2 mb-4">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-10 h-10 rounded-full"
                      onClick={() => handleConfidenceRating(1)}
                      disabled={!isFlipped}
                    >
                      1
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-10 h-10 rounded-full"
                      onClick={() => handleConfidenceRating(2)}
                      disabled={!isFlipped}
                    >
                      2
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-10 h-10 rounded-full"
                      onClick={() => handleConfidenceRating(3)}
                      disabled={!isFlipped}
                    >
                      3
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-10 h-10 rounded-full"
                      onClick={() => handleConfidenceRating(4)}
                      disabled={!isFlipped}
                    >
                      4
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-10 h-10 rounded-full"
                      onClick={() => handleConfidenceRating(5)}
                      disabled={!isFlipped}
                    >
                      5
                    </Button>
                  </div>
                  
                  <div className="flex justify-between">
                    <Button 
                      variant="outline" 
                      onClick={handlePrevious}
                      disabled={currentCard === 0}
                    >
                      Previous
                    </Button>
                    
                    <div className="flex items-center">
                      <span className="text-sm text-gray-500">
                        {currentCard + 1} of {activeSet.cards.length}
                      </span>
                    </div>
                    
                    <Button 
                      variant="outline" 
                      onClick={handleNext}
                      disabled={currentCard === activeSet.cards.length - 1}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col items-center justify-center h-full py-16 px-4 bg-gray-50 border border-dashed border-gray-300 rounded-lg">
              <FlipVertical className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-800 mb-2">No Flashcard Set Selected</h3>
              <p className="text-gray-600 text-center mb-6">
                Select a flashcard set from the sidebar or create a new one to get started.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                Create New Flashcards
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}