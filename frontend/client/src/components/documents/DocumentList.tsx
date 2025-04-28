import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Search, 
  SlidersHorizontal, 
  FileText, 
  FileCode, 
  MoreHorizontal,
  HelpCircle,
  FlipVertical,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

interface DocumentListProps {
  documents: any[];
  isLoading: boolean;
  error: Error | null;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export default function DocumentList({
  documents,
  isLoading,
  error,
  searchQuery,
  onSearchChange,
}: DocumentListProps) {
  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-blue-500" />;
      case 'md':
        return <FileCode className="h-5 w-5 text-green-500" />;
      case 'docx':
        return <FileText className="h-5 w-5 text-indigo-500" />;
      case 'txt':
        return <FileText className="h-5 w-5 text-gray-500" />;
      default:
        return <FileText className="h-5 w-5 text-gray-500" />;
    }
  };
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };
  
  const getFileTypeBadgeColor = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return "bg-blue-100 text-blue-800";
      case 'md':
        return "bg-green-100 text-green-800";
      case 'docx':
        return "bg-indigo-100 text-indigo-800";
      case 'txt':
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle>Your Documents</CardTitle>
        <div className="flex space-x-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search documents..."
              className="w-full md:w-64 pl-9"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
            />
          </div>
          <Button variant="ghost" size="icon">
            <SlidersHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error ? (
          <div className="py-8 text-center">
            <p className="text-red-500 mb-2">Error loading documents</p>
            <p className="text-sm text-gray-500">{error.message}</p>
            <Button className="mt-4" variant="outline" onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        ) : isLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4">
                <Skeleton className="h-12 w-12 rounded" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[250px]" />
                  <Skeleton className="h-4 w-[200px]" />
                </div>
              </div>
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="py-8 text-center">
            <p className="text-gray-500 mb-2">No documents found</p>
            <p className="text-sm text-gray-400">Upload your first document to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Document</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Chunks</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc, index) => (
                  <TableRow key={index} className="hover:bg-gray-50 transition-colors duration-150">
                    <TableCell>
                      <div className="flex items-center">
                        <div className="w-8 h-8 flex-shrink-0 mr-3 bg-blue-100 rounded flex items-center justify-center">
                          {getFileIcon(doc.filetype)}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getFileTypeBadgeColor(doc.filetype)} variant="outline">
                        {doc.filetype.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {formatDate(doc.upload_time)}
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {doc.chunk_count}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button size="icon" variant="ghost" className="text-primary hover:text-indigo-800">
                                <HelpCircle className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Generate Quiz</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                        
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button size="icon" variant="ghost" className="text-primary hover:text-indigo-800">
                                <FlipVertical className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Generate Flashcards</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                        
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button size="icon" variant="ghost" className="text-gray-600 hover:text-gray-900">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>Create Study Session</DropdownMenuItem>
                            <DropdownMenuItem>Download</DropdownMenuItem>
                            <DropdownMenuItem className="text-red-500">Delete</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
