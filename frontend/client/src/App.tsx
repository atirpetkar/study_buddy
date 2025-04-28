import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import Sidebar from "@/components/layout/Sidebar";
import MobileNav from "@/components/layout/MobileNav";
import DashboardPage from "@/pages/DashboardPage";
import DocumentsPage from "@/pages/DocumentsPage";
import SessionsPage from "@/pages/SessionsPage";
import StudySessionPage from "@/pages/StudySessionPage";
import CreateSessionPage from "@/pages/CreateSessionPage";
import ChatPage from "@/pages/ChatPage";
import QuizzesPage from "@/pages/QuizzesPage";
import FlashcardsPage from "@/pages/FlashcardsPage";

function Router() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-gray-50 pb-16 md:pb-0">
        <Switch>
          <Route path="/" component={DashboardPage} />
          <Route path="/documents" component={DocumentsPage} />
          <Route path="/sessions" component={SessionsPage} />
          <Route path="/session/:id" component={StudySessionPage} />
          <Route path="/create-session" component={CreateSessionPage} />
          <Route path="/chat" component={ChatPage} />
          <Route path="/quizzes" component={QuizzesPage} />
          <Route path="/flashcards" component={FlashcardsPage} />
          <Route component={NotFound} />
        </Switch>
      </main>
      <MobileNav />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
