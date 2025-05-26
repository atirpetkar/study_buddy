import { apiRequest } from '../queryClient';
import { API_BASE_URL } from '../config';
import { logApiError, formatErrorMessage } from '../errorHandler';

// Document Management
export const uploadDocuments = async (files: FileList) => {
  try {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    
    console.log('Uploading documents to:', `${API_BASE_URL}/vectorstore/upload`);
    
    const response = await fetch(`${API_BASE_URL}/vectorstore/upload`, {
      method: 'POST',
      body: formData,
      // Don't use include for cross-origin requests if not needed
      credentials: 'omit',
      // Ensure no CORS headers are added automatically
      mode: 'cors',
    });
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || 'Failed to upload documents');
    }
    
    return response.json();
  } catch (error) {
    logApiError(error, 'uploadDocuments');
    throw new Error(formatErrorMessage(error, 'Failed to upload documents'));
  }
};

export const getDocuments = async () => {
  try {
    console.log('Getting documents from:', `${API_BASE_URL}/vectorstore/documents`);
    
    const response = await fetch(`${API_BASE_URL}/vectorstore/documents`, {
      method: 'GET',
      // Don't use include for cross-origin requests if not needed
      credentials: 'omit',
      // Ensure no CORS headers are added automatically
      mode: 'cors',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Document fetch error response:', errorText);
      throw new Error(`Error ${response.status}: ${errorText || response.statusText}`);
    }
    
    return response.json();
  } catch (error) {
    logApiError(error, 'getDocuments');
    throw new Error(formatErrorMessage(error, 'Failed to retrieve documents'));
  }
};

export const documentService = {
  uploadDocuments,
  getDocuments,
}; 