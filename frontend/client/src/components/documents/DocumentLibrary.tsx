import { useState } from "react";
import DocumentUpload from "./DocumentUpload";
import DocumentList from "./DocumentList";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getDocuments, uploadDocuments } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function DocumentLibrary() {
  const [searchQuery, setSearchQuery] = useState("");
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['/api/vectorstore/documents'],
    queryFn: getDocuments,
  });
  
  const uploadMutation = useMutation({
    mutationFn: uploadDocuments,
    onSuccess: () => {
      toast({
        title: "Documents Uploaded",
        description: "Your documents have been uploaded successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/vectorstore/documents'] });
    },
    onError: (error) => {
      toast({
        title: "Upload Failed",
        description: error.message || "There was an error uploading your documents.",
        variant: "destructive",
      });
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
