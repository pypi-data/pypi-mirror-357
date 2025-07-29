import React from 'react';

interface ResponseDisplayProps {
  response: string;
}

export default function ResponseDisplay({ response }: ResponseDisplayProps) {
  if (!response) return null;

  return (
    <div className="mt-4 p-4 border rounded bg-gray-100">
      <h2 className="font-bold text-gray-800">Response:</h2>
      <p className="text-gray-800">{response}</p>
    </div>
  );
}
