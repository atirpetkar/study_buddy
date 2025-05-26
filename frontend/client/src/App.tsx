import { Switch, Route, useLocation } from "wouter";
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
import IntegrationTest from "@/components/IntegrationTest";
import { AuthProvider } from "./context/AuthContext";
import { useEffect } from "react";

// Create a simple verification page
const VerifyPage = () => (
  <div className="p-8">
    <h1 className="text-2xl font-bold mb-6">Integration Verification</h1>
    <IntegrationTest />
  </div>
);

// Login page component (commented out for now since we're bypassing auth)
const LoginPage = () => (
  <div className="p-8">
    <h1 className="text-2xl font-bold mb-6">Login is disabled</h1>
    <p>Authentication has been temporarily disabled. You will be redirected to the dashboard.</p>
    <RedirectToDashboard />
  </div>
);

// Redirect component that automatically sends users to the dashboard
const RedirectToDashboard = () => {
  const [, setLocation] = useLocation();
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setLocation('/');
    }, 1000);
    return () => clearTimeout(timer);
  }, [setLocation]);
  
  return null;
};

// Register page component (commented out for now since we're bypassing auth)
const RegisterPage = () => (
  <div className="p-8">
    <h1 className="text-2xl font-bold mb-6">Registration is disabled</h1>
    <p>Authentication has been temporarily disabled. You will be redirected to the dashboard.</p>
    <RedirectToDashboard />
  </div>
);

// Modified to always return the component without authentication check
function ProtectedRoute({ component: Component, ...rest }: any) {
  // Always render the component without authentication checks
  return <Component {...rest} />;
}

function Router() {
  // Always show the main app with sidebar, bypassing authentication check
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
          <Route path="/verify" component={VerifyPage} />
          <Route path="/login" component={LoginPage} />
          <Route path="/register" component={RegisterPage} />
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
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
