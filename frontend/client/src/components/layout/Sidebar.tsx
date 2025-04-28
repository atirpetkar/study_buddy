import { Link, useLocation } from "wouter";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

const navItems = [
  { name: "Dashboard", path: "/", icon: "ri-dashboard-line" },
  { name: "Document Library", path: "/documents", icon: "ri-file-list-line" },
  { name: "Study Sessions", path: "/sessions", icon: "ri-time-line" },
  { name: "Quizzes", path: "/quizzes", icon: "ri-question-line" },
  { name: "Flashcards", path: "/flashcards", icon: "ri-file-card-line" },
  { name: "AI Tutor Chat", path: "/chat", icon: "ri-chat-3-line" },
];

export default function Sidebar() {
  const [location] = useLocation();

  return (
    <aside className="hidden md:flex md:flex-col md:w-64 bg-white border-r border-gray-200 transition-all duration-300">
      <div className="flex items-center justify-center h-16 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <span className="text-2xl text-primary">
            <i className="ri-book-open-line"></i>
          </span>
          <h1 className="text-xl font-bold text-gray-800">Study Buddy</h1>
        </div>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <Link key={item.path} href={item.path}>
            <a
              className={cn(
                "flex items-center px-4 py-3 rounded-md",
                location === item.path
                  ? "text-gray-800 bg-gray-100"
                  : "text-gray-600 hover:bg-gray-100"
              )}
            >
              <i className={cn(item.icon, "mr-3", location === item.path ? "text-primary" : "")}></i>
              <span>{item.name}</span>
            </a>
          </Link>
        ))}
      </nav>
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="flex items-center">
          <Avatar className="h-10 w-10">
            <AvatarImage src="https://github.com/shadcn.png" alt="User" />
            <AvatarFallback>US</AvatarFallback>
          </Avatar>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-800">Alex Johnson</p>
            <p className="text-xs text-gray-500">alex@example.com</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
