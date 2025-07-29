export const apiUrl = process.env.API_URL || 'http://localhost:8080';

export async function fetchThreads() {
  const res = await fetch(`${apiUrl}/chat`);
  if (!res.ok) {
    throw new Error('Failed to fetch thread IDs');
  }
  return res.json();
}

export async function deleteThread(threadId: string) {
  const res = await fetch(`${apiUrl}/chat/${threadId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete thread');
  }
  return res.json();
}

export async function sendMessage(threadId: string, message: string) {
  const res = await fetch(`${apiUrl}/chat/${threadId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: message }),
  });
  if (!res.ok) {
    throw new Error('Failed to send message');
  }
  return res.json();
}

export async function sendHumanReview(
  threadId: string,
  review: { action: string; data: string }
) {
  const res = await fetch(`${apiUrl}/chat/${threadId}/human_review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(review),
  });
  if (!res.ok) {
    throw new Error('Failed to send human review');
  }
  return res.json();
}
