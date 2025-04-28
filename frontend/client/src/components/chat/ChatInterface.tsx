import { useState, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Send, 
  PaperclipIcon, 
  Mic, 
  Bot, 
  Info, 
  FileText 
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useMutation } from "@tanstack/react-query";
import { sendChatMessage } from "@/lib/api";

type Message = {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
  context_used?: string[];
};

type ChatMode = 'tutor' | 'chat' | 'quiz' | 'flashcard';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      sender: 'ai',
      text: "Hello! I'm your AI study assistant. I can help you learn about topics from your uploaded documents. What would you like to explore today?",
      timestamp: new Date(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [chatMode, setChatMode] = useState<ChatMode>('tutor');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const chatMutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: 'ai',
          text: data.response,
          timestamp: new Date(),
          context_used: data.context_used,
        }
      ]);
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    },
  });
  
  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;
    
    // Add user message to chat
    const newUserMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: inputMessage,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    
    // Clear input field
    setInputMessage('');
    
    // Send to API
    chatMutation.mutate({
      user_id: 'user123', // In a real app, this would come from auth
      message: inputMessage,
      mode: chatMode,
    });
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-4 border-b border-gray-200 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-xl font-bold text-gray-800">AI Tutor Chat</h1>
        </div>
        <div className="flex items-center space-x-3">
          <Select value={chatMode} onValueChange={(value) => setChatMode(value as ChatMode)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Select mode" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="tutor">Tutor Mode</SelectItem>
              <SelectItem value="chat">Chat Mode</SelectItem>
              <SelectItem value="quiz">Quiz Mode</SelectItem>
              <SelectItem value="flashcard">Flashcard Mode</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="ghost" size="icon">
            <Info className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start ${
              message.sender === 'user' ? 'justify-end' : ''
            }`}
          >
            {message.sender === 'ai' ? (
              <Avatar className="h-8 w-8 mr-3 bg-indigo-500 text-white">
                <Bot className="h-4 w-4" />
              </Avatar>
            ) : null}
            
            <div
              className={`p-3 rounded-lg shadow-sm max-w-3xl ${
                message.sender === 'user'
                  ? 'bg-primary text-white'
                  : 'bg-white text-gray-800'
              }`}
            >
              <p>{message.text}</p>
              
              {message.context_used && message.context_used.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <div className="flex items-center text-xs text-gray-500">
                    <FileText className="h-3 w-3 mr-1" />
                    <span>
                      Using context from: {message.context_used.join(', ')}
                    </span>
                  </div>
                </div>
              )}
            </div>
            
            {message.sender === 'user' ? (
              <Avatar className="h-8 w-8 ml-3 bg-gray-300">
                <AvatarFallback>US</AvatarFallback>
              </Avatar>
            ) : null}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-end">
          <div className="flex-1 relative">
            <Textarea
              rows={2}
              placeholder="Type your message here..."
              className="w-full px-4 py-2 resize-none"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={chatMutation.isPending}
            />
            <div className="absolute right-3 bottom-3 flex space-x-2 text-gray-400">
              <Button variant="ghost" size="icon" className="h-6 w-6 hover:text-gray-600" title="Upload file">
                <PaperclipIcon className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-6 w-6 hover:text-gray-600" title="Record audio">
                <Mic className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <Button
            className="ml-3 bg-primary hover:bg-indigo-700 text-white p-3 h-auto"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || chatMutation.isPending}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
