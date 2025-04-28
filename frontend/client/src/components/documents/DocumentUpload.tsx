import { useRef, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DocumentUploadProps {
  onUpload: (files: FileList) => void;
  isUploading: boolean;
}

export default function DocumentUpload({ onUpload, isUploading }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndUpload(e.dataTransfer.files);
    }
  };
  
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndUpload(e.target.files);
    }
  };
  
  const validateAndUpload = (files: FileList) => {
    // Check file types
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
    const validExtensions = ['.pdf', '.docx', '.txt', '.md'];
    
    const invalidFiles = Array.from(files).filter(file => {
      const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      return !validTypes.includes(file.type) && !validExtensions.includes(extension);
    });
    
    if (invalidFiles.length > 0) {
      toast({
        title: "Invalid file types",
        description: "Please upload only PDF, DOCX, TXT, or MD files.",
        variant: "destructive",
      });
      return;
    }
    
    onUpload(files);
  };
  
  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };
  
  return (
    <Card 
      className={`mb-8 border-2 border-dashed ${isDragging ? 'border-primary' : 'border-gray-300'} hover:border-primary transition-colors duration-200`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleButtonClick}
    >
      <div className="flex flex-col items-center justify-center py-10 px-6">
        <i className="ri-upload-cloud-2-line text-5xl text-gray-400 mb-4"></i>
        <h3 className="text-lg font-medium text-gray-800 mb-1">Upload Documents</h3>
        <p className="text-sm text-gray-600 mb-4 text-center">Drag and drop your files here, or click to browse</p>
        <p className="text-xs text-gray-500 text-center">Supported formats: PDF, DOCX, TXT, MD</p>
        <input 
          type="file" 
          ref={fileInputRef}
          className="hidden" 
          multiple 
          accept=".pdf,.docx,.txt,.md" 
          onChange={handleFileInputChange}
          disabled={isUploading}
        />
        <Button 
          className="mt-4" 
          disabled={isUploading} 
          onClick={(e) => e.stopPropagation()}
        >
          {isUploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Select Files
            </>
          )}
        </Button>
      </div>
    </Card>
  );
}
