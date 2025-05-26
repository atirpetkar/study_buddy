import { useState, useEffect, useRef } from "react";
import { useLocation } from "wouter";
import { useQueryClient, useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, RefreshCw } from "lucide-react";
import { getDocuments, createQuickSession } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { DEFAULT_USER_ID, API_BASE_URL } from "@/lib/config";

const formSchema = z.object({
  topic: z.string().min(3, "Topic must be at least 3 characters"),
  description: z.string().optional(),
  duration_minutes: z.string().transform((val) => Number(val)),
  documents: z.array(z.string()).optional(),
  activities: z.array(z.string()).min(1, "Select at least one activity"),
});

export default function CreateSession() {
  const [_, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [creationStatus, setCreationStatus] = useState("");
  const pollingCountRef = useRef(0);
  
  const { data: documentsData, isLoading: loadingDocuments } = useQuery({
    queryKey: ['/api/vectorstore/documents'],
    queryFn: getDocuments,
  });
  
  const createMutation = useMutation({
    mutationFn: createQuickSession,
  });
  
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      topic: "",
      description: "",
      duration_minutes: "15",
      documents: [],
      activities: ["introduction", "flashcard", "quiz", "summary"],
    },
  });
  
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      console.log("Form submitted with values:", values);
      setCreationStatus("Initializing session...");
      
      // Convert string duration to number for API
      const sessionParams = {
        user_id: DEFAULT_USER_ID,
        topic: values.topic,
        duration_minutes: parseInt(values.duration_minutes),
      };
      console.log("Sending to API with parameters:", sessionParams);
      
      const sessionData = await createMutation.mutateAsync(sessionParams);
      console.log("Session created successfully with ID:", sessionData.session_id);
      
      // Start polling for session status
      await pollSessionStatus(sessionData.session_id);
    } catch (error) {
      console.error("Error in session creation:", error);
      toast({
        title: "Session Creation Failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
      setCreationStatus("");
    }
  };
  
  const pollSessionStatus = async (sessionId: string) => {
    const MAX_POLLS = 30; // Increased to allow more time
    const POLL_INTERVAL = 1500; // 1.5 seconds
    
    console.log(`Starting to poll for session status: ${sessionId}`);
    pollingCountRef.current = 0;
    
    const checkStatus = async () => {
      try {
        pollingCountRef.current += 1;
        console.log(`Poll attempt ${pollingCountRef.current}/${MAX_POLLS} for session: ${sessionId}`);
        
        if (pollingCountRef.current >= MAX_POLLS) {
          console.log(`Polling timeout reached for session: ${sessionId}`);
          toast({
            title: "Session Creation Taking Longer Than Expected",
            description: "The session is still being created in the background. You can check your sessions list later.",
            variant: "destructive",
          });
          setCreationStatus("");
          queryClient.invalidateQueries({ queryKey: ['/session/user'] });
          setLocation('/sessions');
          return;
        }
        
        // Fetch current session status - fixed URL to include API_BASE_URL
        const url = `${API_BASE_URL}/session/${sessionId}`;
        console.log(`Polling URL: ${url}`);
        
        setCreationStatus(`Preparing your session... (attempt ${pollingCountRef.current}/${MAX_POLLS})`);
        
        const response = await fetch(url);
        console.log(`Poll response status: ${response.status}`);
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error(`Poll error: ${response.status}`, errorData);
          throw new Error(errorData.detail || `Server error: ${response.status}`);
        }
        
        const sessionData = await response.json();
        console.log(`Poll response data:`, sessionData);
        
        // Use status_message from backend if available
        if (sessionData.status_message) {
          setCreationStatus(sessionData.status_message);
        } else if (sessionData.elapsed_time_seconds) {
          setCreationStatus(`Creating session... (${Math.round(sessionData.elapsed_time_seconds)}s elapsed)`);
        }
        
        // Check session status
        if (sessionData.status === "error") {
          toast({
            title: "Session Creation Failed",
            description: sessionData.error_message || "An error occurred creating the session",
            variant: "destructive",
          });
          setCreationStatus("");
          queryClient.invalidateQueries({ queryKey: ['/session/user'] });
          setLocation('/sessions');
          return;
        }
        
        if (sessionData.status === "planned" || sessionData.status === "in_progress") {
          // Session created successfully
          toast({
            title: "Success",
            description: "Study session created successfully",
          });
          setCreationStatus("");
          queryClient.invalidateQueries({ queryKey: ['/session/user'] });
          setLocation(`/session/${sessionId}`);
          return;
        }
        
        // If still initializing, continue polling
        if (sessionData.status === "initializing") {
          setTimeout(checkStatus, POLL_INTERVAL);
        } else {
          // Unknown status
          toast({
            title: "Unknown Status",
            description: `Session has unknown status: ${sessionData.status}`,
            variant: "destructive",
          });
          setCreationStatus("");
          queryClient.invalidateQueries({ queryKey: ['/session/user'] });
          setLocation('/sessions');
        }
      } catch (error) {
        console.error("Error polling session status:", error);
        // If there's an error, try again unless we've reached the limit
        if (pollingCountRef.current < MAX_POLLS) {
          setTimeout(checkStatus, POLL_INTERVAL);
        } else {
          toast({
            title: "Failed to Check Status",
            description: "Could not verify if the session was created. Please check your sessions list.",
            variant: "destructive",
          });
          setCreationStatus("");
          queryClient.invalidateQueries({ queryKey: ['/session/user'] });
          setLocation('/sessions');
        }
      }
    };
    
    // Start polling
    setTimeout(checkStatus, POLL_INTERVAL);
  };
  
  return (
    <div className="px-4 py-6 md:px-8">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/")} className="mr-2">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-2xl font-bold text-gray-800">Create Study Session</h1>
        </div>
      </div>
      
      <Card className="mb-8">
        <CardContent className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="topic"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Topic</FormLabel>
                    <FormControl>
                      <Input placeholder="e.g., Machine Learning Basics" {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description (optional)</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Brief description of what you want to learn" 
                        className="resize-none" 
                        {...field} 
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="duration_minutes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Duration</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value.toString()}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select duration" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="15">15 minutes</SelectItem>
                        <SelectItem value="30">30 minutes</SelectItem>
                        <SelectItem value="45">45 minutes</SelectItem>
                        <SelectItem value="60">60 minutes</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="documents"
                render={() => (
                  <FormItem>
                    <FormLabel>Source Documents</FormLabel>
                    <div className="space-y-2">
                      {loadingDocuments ? (
                        <p className="text-sm text-gray-500">Loading documents...</p>
                      ) : !documentsData?.documents?.length ? (
                        <p className="text-sm text-gray-500">No documents available. Upload some first.</p>
                      ) : (
                        documentsData.documents.map((doc: any, index: number) => (
                          <div key={index} className="flex items-center">
                            <FormField
                              control={form.control}
                              name="documents"
                              render={({ field }) => (
                                <FormItem className="flex items-center space-x-2 space-y-0">
                                  <FormControl>
                                    <Checkbox
                                      checked={field.value?.includes(doc.filename)}
                                      onCheckedChange={(checked) => {
                                        return checked
                                          ? field.onChange([...field.value || [], doc.filename])
                                          : field.onChange(field.value?.filter((value) => value !== doc.filename));
                                      }}
                                    />
                                  </FormControl>
                                  <FormLabel className="text-sm font-normal cursor-pointer">
                                    {doc.filename}
                                  </FormLabel>
                                </FormItem>
                              )}
                            />
                          </div>
                        ))
                      )}
                    </div>
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="activities"
                render={() => (
                  <FormItem>
                    <FormLabel>Activity Preferences</FormLabel>
                    <div className="space-y-4 mt-3">
                      {[
                        { id: "introduction", title: "Introduction", desc: "Overview of the topic" },
                        { id: "flashcard", title: "Flashcards", desc: "Review key concepts" },
                        { id: "quiz", title: "Quiz", desc: "Test your knowledge" },
                        { id: "summary", title: "Summary", desc: "Wrap-up and key takeaways" }
                      ].map((activity) => (
                        <div 
                          key={activity.id} 
                          className="flex items-center justify-between p-3 border border-gray-200 rounded-md"
                        >
                          <div>
                            <h4 className="font-medium text-gray-800">{activity.title}</h4>
                            <p className="text-sm text-gray-600">{activity.desc}</p>
                          </div>
                          <FormField
                            control={form.control}
                            name="activities"
                            render={({ field }) => (
                              <FormItem className="flex items-center space-x-2 space-y-0">
                                <FormControl>
                                  <Checkbox
                                    checked={field.value?.includes(activity.id)}
                                    onCheckedChange={(checked) => {
                                      return checked
                                        ? field.onChange([...field.value || [], activity.id])
                                        : field.onChange(field.value?.filter((value) => value !== activity.id));
                                    }}
                                  />
                                </FormControl>
                              </FormItem>
                            )}
                          />
                        </div>
                      ))}
                    </div>
                  </FormItem>
                )}
              />
              
              <div className="flex justify-end items-center">
                {creationStatus && (
                  <div className="flex items-center mr-4 text-sm text-gray-600">
                    <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                    {creationStatus}
                  </div>
                )}
                <Button 
                  type="submit" 
                  disabled={createMutation.isPending || Boolean(creationStatus)}
                  className="bg-primary hover:bg-indigo-700"
                >
                  {createMutation.isPending || creationStatus ? "Creating..." : "Create Session"}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
