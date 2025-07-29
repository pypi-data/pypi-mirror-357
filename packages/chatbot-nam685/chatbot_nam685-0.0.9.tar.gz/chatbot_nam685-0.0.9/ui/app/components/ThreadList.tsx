import React from 'react';
import { Thread } from '../models';

interface ThreadListProps {
  threads: Thread[];
  selectedThread: Thread | null;
  setSelectedThread: (thread: Thread) => void;
  deleteThread: (threadId: string) => void;
}

export default function ThreadList({
  threads,
  selectedThread,
  setSelectedThread,
  deleteThread,
}: ThreadListProps) {
  return (
    <ul className="list-disc w-full">
      {threads.map((thread) => (
        <li key={thread.thread_id} className="mb-2">
          <div className="flex justify-between items-center w-full">
            <button
              onClick={() => setSelectedThread(thread)}
              className={`flex-grow flex justify-between items-center px-4 py-2 border rounded ${
                selectedThread === thread ? 'bg-blue-100' : 'bg-gray-100'
              } hover:bg-blue-300`}
            >
              <span className="font-medium text-gray-800">
                {thread.thread_id}
              </span>
              <span
                className={`text-sm px-2 py-1 rounded ${
                  thread.status === 'interrupted'
                    ? 'bg-red-200 text-red-800'
                    : 'bg-green-200 text-green-800'
                }`}
              >
                {thread.status}
              </span>
            </button>
            <button
              onClick={() => deleteThread(thread.thread_id)}
              className="ml-2 px-3 py-2 text-white bg-red-500 rounded hover:bg-red-600"
            >
              Delete
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
