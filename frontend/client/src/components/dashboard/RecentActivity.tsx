import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { Link } from "wouter";

type Activity = {
  type: string;
  title: string;
  time: string;
  duration?: string;
  detail?: string;
  icon: string;
  iconBg: string;
  iconColor: string;
};

interface RecentActivityProps {
  activities: Activity[];
}

export default function RecentActivity({ activities }: RecentActivityProps) {
  return (
    <Card className="mb-8">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle>Recent Activity</CardTitle>
        <Link href="/activities">
          <a className="text-primary text-sm font-medium hover:text-indigo-700">View All</a>
        </Link>
      </CardHeader>
      <CardContent>
        {activities.map((activity, index) => (
          <div key={index} className={cn(
            index < activities.length - 1 ? "border-b border-gray-100" : "",
            "py-3"
          )}>
            <div className="flex items-center">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center",
                activity.iconBg,
                activity.iconColor
              )}>
                <i className={activity.icon}></i>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-800">{activity.title}</p>
                <p className="text-xs text-gray-500">
                  {activity.time}
                  {activity.duration && ` · ${activity.duration}`}
                  {activity.detail && ` · ${activity.detail}`}
                </p>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
