import { useState } from "react";
import DocumentUpload from "./DocumentUpload";
import DocumentList from "./DocumentList";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { documentService } from "@/lib/services/documentService";
import { useAuth } from "@/context/AuthContext";

export default function DocumentLibrary() {
  const [searchQuery, setSearchQuery] = useState("");
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: documentService.getDocuments,
  });
  
  const uploadMutation = useMutation({
    mutationFn: documentService.uploadDocuments,
    onSuccess: () => {
      toast({
        title: "Documents Uploaded",
        description: "Your documents have been uploaded successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: (error: any) => {
      toast({
        title: "Upload Failed",
        description: error.message || "There was an error uploading your documents.",
        variant: "destructive",
      });
      console.error("Document upload error:", error);
    }
  });
  
  const handleFileUpload = (files: FileList) => {
    uploadMutation.mutate(files);
  };
  
  const filteredDocuments = data?.documents.filter(
    (doc: any) => doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div className="px-4 py-6 md:px-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Document Library</h1>
      </div>
      
      <DocumentUpload 
        onUpload={handleFileUpload} 
        isUploading={uploadMutation.isPending} 
      />
      
      <DocumentList 
        documents={filteredDocuments || []} 
        isLoading={isLoading} 
        error={error as Error | null} 
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />
    </div>
  );
}
