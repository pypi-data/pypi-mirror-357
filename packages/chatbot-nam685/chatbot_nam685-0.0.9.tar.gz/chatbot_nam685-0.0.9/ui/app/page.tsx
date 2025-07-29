'use client';

import { v4 as uuidv4 } from 'uuid';
import { useState } from 'react';
import ThreadList from './components/ThreadList';
import MessageInput from './components/MessageInput';
import HumanReviewForm from './components/HumanReviewForm';
import ResponseDisplay from './components/ResponseDisplay';
import {
  fetchThreads,
  deleteThread,
  sendMessage,
  sendHumanReview,
} from './utils/chat';
import { Thread, HumanReview } from './models';

export default function Home() {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [selectedThread, setSelectedThread] = useState<Thread | null>(null);
  const [message, setMessage] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [humanReview, setHumanReview] = useState<HumanReview>(
    new HumanReview('continue', '')
  );
  const [response, setResponse] = useState<string>('');

  const handleFetchThreads = async () => {
    try {
      const data = await fetchThreads();
      const threads = data.map(
        (thread: { thread_id: string; status: string }) =>
          new Thread(thread.thread_id, thread.status)
      );
      setThreads(threads);
    } catch (error) {
      console.error('Error fetching thread IDs:', error);
    }
  };

  const handleDeleteThread = async (threadId: string) => {
    try {
      await deleteThread(threadId);
      setThreads((prevThreads) =>
        prevThreads.filter(
          (thread: { thread_id: string; status: string }) =>
            thread.thread_id !== threadId
        )
      );
      if (selectedThread?.thread_id === threadId) {
        setSelectedThread(null);
        setResponse('');
      }
    } catch (error) {
      console.error('Error deleting thread:', error);
    }
  };

  const updateThreadStatusAndResponse = async (
    resData: { type: string; data: string },
    oldThread: Thread
  ) => {
    const thread = new Thread(
      oldThread.thread_id,
      resData['type'] === 'interrupt' ? 'interrupted' : 'idle'
    );
    setSelectedThread(thread);
    setThreads((prevThreads) =>
      prevThreads.map((t) => (t.thread_id === oldThread.thread_id ? thread : t))
    );
    if (resData['type'] === 'interrupt') {
      setResponse('');
      setSearchQuery(resData['data']);
    } else if (resData['type'] === 'message') {
      setResponse(resData['data']);
      setSearchQuery('');
    } else {
      throw new Error('Unexpected response type');
    }
  };

  const handleSendMessage = async () => {
    if (!selectedThread || !message) {
      alert('Please select a thread and enter a message.');
      return;
    }
    try {
      const resData = await sendMessage(selectedThread.thread_id, message);
      await updateThreadStatusAndResponse(resData, selectedThread);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleSendHumanReview = async () => {
    if (!selectedThread || !humanReview) {
      alert('Please select a thread and specify an action.');
      return;
    }
    try {
      const resData = await sendHumanReview(
        selectedThread.thread_id,
        humanReview
      );
      await updateThreadStatusAndResponse(resData, selectedThread);
    } catch (error) {
      console.error('Error sending human review:', error);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <h1 className="text-2xl font-bold">Chatbot</h1>
      <div className="flex gap-4">
        <button
          onClick={handleFetchThreads}
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          List Threads
        </button>
        <button
          onClick={() =>
            setThreads((prev) => [...prev, new Thread(uuidv4(), 'idle')])
          }
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          New Thread
        </button>
      </div>
      <ThreadList
        threads={threads}
        selectedThread={selectedThread}
        setSelectedThread={setSelectedThread}
        deleteThread={handleDeleteThread}
      />
      {selectedThread && (
        <>
          {selectedThread.status === 'interrupted' ? (
            <HumanReviewForm
              searchQuery={searchQuery}
              humanReview={humanReview}
              setHumanReview={setHumanReview}
              sendHumanReview={handleSendHumanReview}
            />
          ) : (
            <MessageInput
              message={message}
              setMessage={setMessage}
              sendMessage={handleSendMessage}
            />
          )}
        </>
      )}
      <ResponseDisplay response={response} />
    </div>
  );
}
