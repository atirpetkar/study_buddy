import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../lib/config';
import { documentService } from '@/lib/services/documentService';
import { chatService } from '@/lib/services/chatService';
import { debugService } from '@/lib/services/debugService';
import { Button } from './ui/button';
import { DEFAULT_USER_ID } from '@/lib/config';

// Add a new section for API endpoint testing with POST support
const ApiEndpointTest = ({ endpoint, label, supportPost = false }: { endpoint: string; label: string; supportPost?: boolean }) => {
  const [testStatus, setTestStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [postStatus, setPostStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [statusCode, setStatusCode] = useState<number | null>(null);
  const [postStatusCode, setPostStatusCode] = useState<number | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [postResponseTime, setPostResponseTime] = useState<number | null>(null);
  const [message, setMessage] = useState<string>('');
  const [postMessage, setPostMessage] = useState<string>('');
  const [postResponse, setPostResponse] = useState<any>(null);

  const testEndpoint = async () => {
    setTestStatus('loading');
    try {
      const result = await debugService.pingEndpoint(endpoint);
      console.log(`Endpoint test result for ${endpoint}:`, result);
      
      if (result.success) {
        setTestStatus('success');
        setStatusCode(result.status || 200);
      } else {
        setTestStatus('error');
        setStatusCode(result.status || 0);
      }
      
      setResponseTime(result.responseTime);
      setMessage(result.message || '');
    } catch (error) {
      console.error(`Endpoint test error for ${endpoint}:`, error);
      setTestStatus('error');
      setMessage(error instanceof Error ? error.message : 'Unknown error');
    }
  };
  
  const testPostEndpoint = async () => {
    if (!supportPost) return;
    
    setPostStatus('loading');
    
    // For the chat endpoint, use exactly the right format
    if (endpoint === '/chat/chat') {
      // Use exactly the format that matches the backend ChatRequest schema
      const payload = {
        user_id: DEFAULT_USER_ID,
        message: 'Test message for API testing',
        mode: 'chat'
      };
      
      try {
        console.log(`Testing chat with standard payload:`, payload);
        const result = await debugService.testPostEndpoint(endpoint, payload);
        
        if (result.success) {
          console.log(`POST endpoint test success!`);
          setPostStatus('success');
          setPostStatusCode(result.status || 200);
          setPostResponseTime(result.responseTime);
          setPostMessage(`Success with standard chat payload`);
          setPostResponse(result.response);
          return;
        } else {
          setPostStatus('error');
          setPostStatusCode(result.status || 0);
          setPostResponseTime(result.responseTime);
          setPostMessage(result.message || 'Failed to send chat message');
          console.error('Chat POST test failed:', result);
        }
      } catch (error) {
        console.error(`POST test error:`, error);
        setPostStatus('error');
        setPostMessage(error instanceof Error ? error.message : String(error));
      }
      return;
    }
    
    // For other endpoints, use a default payload
    const testData = { test: true };
    
    try {
      const result = await debugService.testPostEndpoint(endpoint, testData);
      console.log(`POST endpoint test result for ${endpoint}:`, result);
      
      if (result.success) {
        setPostStatus('success');
        setPostStatusCode(result.status || 200);
      } else {
        setPostStatus('error');
        setPostStatusCode(result.status || 0);
      }
      
      setPostResponseTime(result.responseTime);
      setPostMessage(result.message || '');
      setPostResponse(result.response);
    } catch (error) {
      console.error(`POST endpoint test error for ${endpoint}:`, error);
      setPostStatus('error');
      setPostMessage(error instanceof Error ? error.message : 'Unknown error');
    }
  };

  return (
    <div className="mt-2 border-t pt-2">
      <p className="text-sm font-medium">{label} ({endpoint})</p>
      <div className="flex items-center gap-2 mt-1">
        <Button 
          onClick={testEndpoint} 
          disabled={testStatus === 'loading'} 
          variant="outline" 
          size="sm"
        >
          Test GET
        </Button>
        <span className="text-sm">
          Status: 
          {testStatus === 'idle' && <span className="text-gray-400 ml-1">Not tested</span>}
          {testStatus === 'loading' && <span className="text-blue-500 ml-1">Testing...</span>}
          {testStatus === 'success' && (
            <span className="text-green-500 ml-1">
              OK {statusCode} ({responseTime}ms)
            </span>
          )}
          {testStatus === 'error' && (
            <span className="text-red-500 ml-1">
              Failed {statusCode ? `(${statusCode})` : ''} ({responseTime}ms)
            </span>
          )}
        </span>
      </div>
      {message && (
        <p className="text-xs mt-1 text-gray-600">{message}</p>
      )}
      
      {supportPost && (
        <>
          <div className="flex items-center gap-2 mt-2">
            <Button 
              onClick={testPostEndpoint} 
              disabled={postStatus === 'loading'} 
              variant="outline" 
              size="sm"
            >
              Test POST
            </Button>
            <span className="text-sm">
              Status: 
              {postStatus === 'idle' && <span className="text-gray-400 ml-1">Not tested</span>}
              {postStatus === 'loading' && <span className="text-blue-500 ml-1">Testing...</span>}
              {postStatus === 'success' && (
                <span className="text-green-500 ml-1">
                  OK {postStatusCode} ({postResponseTime}ms)
                </span>
              )}
              {postStatus === 'error' && (
                <span className="text-red-500 ml-1">
                  Failed {postStatusCode ? `(${postStatusCode})` : ''} ({postResponseTime}ms)
                </span>
              )}
            </span>
          </div>
          {postMessage && (
            <p className="text-xs mt-1 text-gray-600">{postMessage}</p>
          )}
          {postResponse && (
            <pre className="text-xs mt-1 bg-gray-100 p-1 rounded max-h-20 overflow-auto">
              {JSON.stringify(postResponse, null, 2)}
            </pre>
          )}
        </>
      )}
    </div>
  );
};

const IntegrationTest = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [timestamp, setTimestamp] = useState('');
  const [errorDetails, setErrorDetails] = useState('');
  
  const [documentStatus, setDocumentStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [documentMessage, setDocumentMessage] = useState('');
  
  const [chatStatus, setChatStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [chatMessage, setChatMessage] = useState('');

  // Test direct API call
  const [directApiStatus, setDirectApiStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [directApiMessage, setDirectApiMessage] = useState('');
  const [directApiResponse, setDirectApiResponse] = useState<any>(null);
  
  const testDirectApi = async () => {
    setDirectApiStatus('loading');
    try {
      // Make a direct fetch call to test API
      const url = `${API_BASE_URL}/health`;
      console.log('Making direct API test call to:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        mode: 'cors',
        credentials: 'omit'
      });
      
      console.log('Direct API response:', {
        status: response.status,
        headers: {
          contentType: response.headers.get('content-type'),
          cors: response.headers.get('access-control-allow-origin')
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Direct API response data:', data);
      
      setDirectApiStatus('success');
      setDirectApiMessage('Direct API call successful');
      setDirectApiResponse(data);
    } catch (error) {
      console.error('Direct API test error:', error);
      setDirectApiStatus('error');
      setDirectApiMessage(error instanceof Error ? error.message : 'Unknown error');
    }
  };

  useEffect(() => {
    const checkHealth = async () => {
      try {
        console.log('Making health check request to:', `${API_BASE_URL}/health`);
        
        const response = await fetch(`${API_BASE_URL}/health`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          // Don't use include credentials for the health endpoint
          // as it might not require authentication
          credentials: 'omit',
        });
        
        console.log('Health check response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
          throw new Error(`HTTP error! Status: ${response.status}, Details: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Health check response data:', data);
        
        setStatus('success');
        setMessage(data.message || 'API is running');
        setTimestamp(data.timestamp || new Date().toISOString());
      } catch (error) {
        console.error('Error checking health:', error);
        setStatus('error');
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        setMessage('Connection failed');
        setErrorDetails(errorMessage);
      }
    };

    checkHealth();
  }, []);
  
  const testDocumentService = async () => {
    setDocumentStatus('loading');
    try {
      const result = await documentService.getDocuments();
      console.log('Document service test result:', result);
      setDocumentStatus('success');
      setDocumentMessage(`Successfully retrieved ${result.documents?.length || 0} documents`);
    } catch (error) {
      console.error('Document service test error:', error);
      setDocumentStatus('error');
      setDocumentMessage(error instanceof Error ? error.message : 'Unknown error occurred');
    }
  };
  
  const testChatService = async () => {
    setChatStatus('loading');
    try {
      console.log('Starting chat service test with payload:', {
        user_id: DEFAULT_USER_ID,
        message: 'Hello, this is a test message for integration testing',
        mode: 'chat'
      });

      const result = await chatService.sendMessage({
        user_id: DEFAULT_USER_ID,
        message: 'Hello, this is a test message for integration testing',
        mode: 'chat'
      });
      
      console.log('Chat service test result:', result);
      setChatStatus('success');
      setChatMessage(`Successfully sent message and received: ${result.response?.slice(0, 50)}...`);
    } catch (error) {
      console.error('Chat service test error (detailed):', error);
      setChatStatus('error');
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setChatMessage(errorMessage);
      
      // Try with simple format as fallback
      try {
        console.log('Trying simplified chat format...');
        await testSimpleChatMessage();
      } catch (e) {
        console.error('Simplified chat also failed:', e);
      }
    }
  };
  
  // Test with a simplified message format - includes required user_id and mode fields
  const testSimpleChatMessage = async () => {
    try {
      console.log('Testing simplified chat format with necessary fields...');
      const result = await chatService.sendSimpleMessage('Hello, this is a simple test message');
      
      console.log('Simple chat test result:', result);
      setChatStatus('success');
      setChatMessage(`Successfully sent simple message and received response`);
      return result;
    } catch (error) {
      console.error('Simple chat test error:', error);
      setChatStatus('error');
      setChatMessage(`Simple format also failed: ${error instanceof Error ? error.message : String(error)}`);
      throw error;
    }
  };

  return (
    <div className="p-4 m-4 border rounded-md space-y-6">
      <div>
        <h2 className="text-xl font-bold mb-2">API Health Check</h2>
        <div className="space-y-2">
          <p>
            <span className="font-semibold">Status: </span>
            {status === 'loading' && <span className="text-blue-500">Loading...</span>}
            {status === 'success' && <span className="text-green-500">Connected successfully!</span>}
            {status === 'error' && <span className="text-red-500">Connection failed</span>}
          </p>
          {message && (
            <p>
              <span className="font-semibold">Message: </span>
              {message}
            </p>
          )}
          {timestamp && (
            <p>
              <span className="font-semibold">Server timestamp: </span>
              {new Date(timestamp).toLocaleString()}
            </p>
          )}
          {errorDetails && (
            <p className="text-red-500 mt-2">
              <span className="font-semibold">Error details: </span>
              {errorDetails}
            </p>
          )}
        </div>
      </div>
      
      <div>
        <h2 className="text-xl font-bold mb-2">Document Service Test</h2>
        <div className="space-y-2">
          <Button onClick={testDocumentService} disabled={documentStatus === 'loading'}>
            Test Document Service
          </Button>
          <p>
            <span className="font-semibold">Status: </span>
            {documentStatus === 'idle' && <span className="text-gray-500">Not tested</span>}
            {documentStatus === 'loading' && <span className="text-blue-500">Loading...</span>}
            {documentStatus === 'success' && <span className="text-green-500">Test passed!</span>}
            {documentStatus === 'error' && <span className="text-red-500">Test failed</span>}
          </p>
          {documentMessage && (
            <p>
              <span className="font-semibold">Result: </span>
              {documentMessage}
            </p>
          )}
        </div>
      </div>
      
      <div>
        <h2 className="text-xl font-bold mb-2">Chat Service Test</h2>
        <div className="space-y-2">
          <Button onClick={testChatService} disabled={chatStatus === 'loading'}>
            Test Chat Service
          </Button>
          <p>
            <span className="font-semibold">Status: </span>
            {chatStatus === 'idle' && <span className="text-gray-500">Not tested</span>}
            {chatStatus === 'loading' && <span className="text-blue-500">Loading...</span>}
            {chatStatus === 'success' && <span className="text-green-500">Test passed!</span>}
            {chatStatus === 'error' && <span className="text-red-500">Test failed</span>}
          </p>
          {chatMessage && (
            <p>
              <span className="font-semibold">Result: </span>
              {chatMessage}
            </p>
          )}
        </div>
      </div>
      
      <div>
        <h2 className="text-xl font-bold mb-2">API Endpoint Testing</h2>
        <div className="space-y-2">
          <p className="text-sm text-gray-600 mb-2">
            Test individual API endpoints to identify connectivity issues
          </p>
          
          <ApiEndpointTest endpoint="/health" label="Health Check" />
          <ApiEndpointTest endpoint="/vectorstore/documents" label="Documents API" />
          <ApiEndpointTest endpoint="/chat/chat" label="Chat API" supportPost={true} />
        </div>
      </div>
      
      <div className="mt-4 p-2 bg-gray-100 rounded">
        <p className="font-semibold">Debug Info:</p>
        <p>API_BASE_URL: {API_BASE_URL}</p>
        <p>Default User ID: {DEFAULT_USER_ID}</p>
      </div>
      
      <div>
        <h2 className="text-xl font-bold mb-2">Direct API Test</h2>
        <p className="text-sm text-gray-600 mb-2">
          Test direct API connection bypassing service layers
        </p>
        <div className="space-y-2">
          <Button 
            onClick={testDirectApi} 
            disabled={directApiStatus === 'loading'}
          >
            Test Direct API Call
          </Button>
          <p>
            <span className="font-semibold">Status: </span>
            {directApiStatus === 'idle' && <span className="text-gray-500">Not tested</span>}
            {directApiStatus === 'loading' && <span className="text-blue-500">Loading...</span>}
            {directApiStatus === 'success' && <span className="text-green-500">Success</span>}
            {directApiStatus === 'error' && <span className="text-red-500">Failed</span>}
          </p>
          {directApiMessage && (
            <p>
              <span className="font-semibold">Result: </span>
              {directApiMessage}
            </p>
          )}
          {directApiResponse && (
            <pre className="text-xs mt-1 bg-gray-100 p-1 rounded max-h-20 overflow-auto">
              {JSON.stringify(directApiResponse, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default IntegrationTest;