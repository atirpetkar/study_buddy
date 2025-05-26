import React, { useState } from "react";
import { useLocation, Link } from "wouter";

const API_URL = process.env.REACT_APP_API_URL || "/api";

// Helper function to safely convert any error to a string
const formatErrorMessage = (error: any): string => {
  if (error === null || error === undefined) {
    return "Unknown error occurred";
  }
  
  if (typeof error === "string") {
    return error;
  }
  
  if (Array.isArray(error)) {
    return error.map(item => formatErrorMessage(item)).join(", ");
  }
  
  if (typeof error === "object") {
    // Handle validation errors specifically
    if (error.msg && error.loc) {
      return `${error.msg} at ${error.loc.join('.')}`;
    }
    
    // If it has a 'detail' property, format that
    if (error.detail) {
      return formatErrorMessage(error.detail);
    }
    
    // Try to extract meaningful message from object
    const messages = [];
    for (const key of Object.keys(error)) {
      const value = error[key];
      if (typeof value === "string") {
        messages.push(`${key}: ${value}`);
      } else if (value !== null && value !== undefined) {
        messages.push(`${key}: ${formatErrorMessage(value)}`);
      }
    }
    
    if (messages.length > 0) {
      return messages.join(", ");
    }
    
    // Last resort - stringify the object
    try {
      return JSON.stringify(error);
    } catch {
      return "Error object couldn't be displayed";
    }
  }
  
  return String(error);
};

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [_, setLocation] = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);
    try {
      const res = await fetch(`${API_URL}/users/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      
      const data = await res.json().catch(() => ({}));
      
      if (res.ok) {
        setSuccess(true);
        setTimeout(() => setLocation("/login?registered=1"), 1500);
      } else {
        setError(formatErrorMessage(data) || `Registration failed (${res.status})`);
      }
    } catch (err) {
      setError(formatErrorMessage(err) || "Network error occurred");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded shadow">
        <h2 className="text-2xl font-bold mb-6 text-center">Register</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Email</label>
            <input
              type="email"
              className="w-full border px-3 py-2 rounded"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Password</label>
            <input
              type="password"
              className="w-full border px-3 py-2 rounded"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="text-red-500 text-sm">{error}</div>}
          {success && <div className="text-green-600 text-sm">Registration successful! Redirecting...</div>}
          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700"
          >
            Register
          </button>
        </form>
        <div className="mt-4 text-center">
          <span>Already have an account? </span>
          <Link href="/login" className="text-indigo-600 hover:underline">Login</Link>
        </div>
      </div>
    </div>
  );
}
