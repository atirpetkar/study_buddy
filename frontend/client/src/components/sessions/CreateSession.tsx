import { useState, useEffect } from "react";
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
import { ArrowLeft } from "lucide-react";
import { getDocuments, createQuickSession } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  topic: z.string().min(3, "Topic must be at least 3 characters"),
  description: z.string().optional(),
  duration_minutes: z.string().transform(val => parseInt(val)),
  documents: z.array(z.string()).optional(),
  activities: z.array(z.string()).min(1, "Select at least one activity"),
});

export default function CreateSession() {
  const [_, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const { data: documentsData, isLoading: loadingDocuments } = useQuery({
    queryKey: ['/api/vectorstore/documents'],
    queryFn: getDocuments,
  });
  
  const createMutation = useMutation({
    mutationFn: createQuickSession,
    onSuccess: (data) => {
      toast({
        title: "Session Created",
        description: "Your study session has been created successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/session/user'] });
      setLocation(`/session/${data.session_id}`);
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to create session. Please try again.",
        variant: "destructive",
      });
    },
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
  
  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createMutation.mutate({
      user_id: "user123", // In a real app, this would come from auth
      topic: values.topic,
      duration_minutes: values.duration_minutes,
    });
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
              
              <div className="flex justify-end">
                <Button 
                  type="submit" 
                  disabled={createMutation.isPending}
                  className="bg-primary hover:bg-indigo-700"
                >
                  {createMutation.isPending ? "Creating..." : "Create Session"}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
