import React from 'react';

interface MessageInputProps {
  message: string;
  setMessage: (message: string) => void;
  sendMessage: () => void;
}

export default function MessageInput({
  message,
  setMessage,
  sendMessage,
}: MessageInputProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <textarea
        placeholder="Enter your message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className="border p-2 w-80 h-20"
      />
      <button
        onClick={sendMessage}
        className="px-4 py-2 bg-green-500 text-white rounded"
      >
        Send Message
      </button>
    </div>
  );
}
