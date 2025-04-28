import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";

const navItems = [
  { name: "Home", path: "/", icon: "ri-dashboard-line" },
  { name: "Documents", path: "/documents", icon: "ri-file-list-line" },
  { name: "Sessions", path: "/sessions", icon: "ri-time-line" },
  { name: "Chat", path: "/chat", icon: "ri-chat-3-line" },
];

export default function MobileNav() {
  const [location] = useLocation();

  return (
    <div className="md:hidden fixed bottom-0 inset-x-0 bg-white border-t border-gray-200 z-10">
      <nav className="flex justify-around py-3">
        {navItems.map((item) => (
          <Link key={item.path} href={item.path}>
            <a
              className={cn(
                "flex flex-col items-center",
                location === item.path ? "text-primary" : "text-gray-600"
              )}
            >
              <i className={`${item.icon} text-xl`}></i>
              <span className="text-xs mt-1">{item.name}</span>
            </a>
          </Link>
        ))}
      </nav>
    </div>
  );
}
