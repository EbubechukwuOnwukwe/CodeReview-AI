import type { CreateReviewPayload, Review } from "../types/review";


const API_BASE_URL = "http://localhost:8000/api/reviews/";

export async function createReview(payload: CreateReviewPayload): Promise<Review> {
  const response = await fetch(API_BASE_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message =
      errorData.detail ||
      errorData.repository_url?.[0] ||
      errorData.code?.[0] ||
      errorData.error_message ||
      "Failed to initiate code review.";
    throw new Error(message);
  }

  return response.json();
}

export async function getReview(id: number | string): Promise<Review> {
  const response = await fetch(`${API_BASE_URL}${id}/`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Review #${id} not found.`);
  }

  return response.json();
}

export async function getReviews(): Promise<Review[]> {
  const response = await fetch(API_BASE_URL, {
    method: "GET",
    headers: {
      "Accept": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch reviews history.");
  }

  return response.json();
}

export async function retryReview(id: number | string): Promise<Review> {
  const response = await fetch(`${API_BASE_URL}${id}/retry/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error_message || "Failed to retry code review.");
  }

  return response.json();
}

