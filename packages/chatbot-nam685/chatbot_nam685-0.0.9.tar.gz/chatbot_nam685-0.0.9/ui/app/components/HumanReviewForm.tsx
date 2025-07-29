import React from 'react';
import { HumanReview } from '../models';

interface HumanReviewFormProps {
  searchQuery: string;
  humanReview: HumanReview;
  setHumanReview: (review: HumanReview) => void;
  sendHumanReview: () => void;
}

export default function HumanReviewForm({
  searchQuery,
  humanReview,
  setHumanReview,
  sendHumanReview,
}: HumanReviewFormProps) {
  return (
    <div className="flex flex-col items-center gap-4">
      {/* Display the search query */}
      <p className="text-center">
        Chat model wants to search using this query:{' '}
        <span className="font-bold">{searchQuery}</span>
      </p>

      {/* Human review form */}
      <div className="flex flex-col items-center gap-2">
        <select
          value={humanReview.action}
          onChange={(e) =>
            setHumanReview(new HumanReview(e.target.value, humanReview.data))
          }
          className="border p-2 w-80"
        >
          <option value="continue">Continue</option>
          <option value="feedback">Feedback</option>
        </select>
        {humanReview.action === 'feedback' && (
          <textarea
            placeholder="Enter feedback"
            value={humanReview.data}
            onChange={(e) =>
              setHumanReview(
                new HumanReview(humanReview.action, e.target.value)
              )
            }
            className="border p-2 w-80 h-20"
          />
        )}
        <button
          onClick={sendHumanReview}
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          Submit Human Review
        </button>
      </div>
    </div>
  );
}
