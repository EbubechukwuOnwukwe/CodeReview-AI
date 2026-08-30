import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ReviewForm } from "../components/ReviewForm";
import { createReview } from "../services/api";
import type { CreateReviewPayload } from "../types/review";

export const NewReview = () => {

  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (payload: CreateReviewPayload) => {
    setIsLoading(true);
    try {
      const review = await createReview(payload);
      navigate(`/review/${review.id}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white">Submit Code Review</h1>
        <p className="text-slate-400 text-sm">
          Provide a GitHub repository link or paste code snippets to run full agentic verification
        </p>
      </div>

      <ReviewForm onSubmit={handleSubmit} isLoading={isLoading} />
    </div>
  );
};
