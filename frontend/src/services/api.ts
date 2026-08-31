import type {
  CreateReviewPayload,
  Review,
} from "../types/review";


const API_BASE_URL =
  "http://localhost:8000/api/reviews/";


const GENERIC_REVIEW_ERROR =
  "We couldn't complete this code review right now. Please try again in a moment.";


export async function createReview(
  payload: CreateReviewPayload
): Promise<Review> {

  const response = await fetch(
    API_BASE_URL,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },

      body: JSON.stringify(payload),
    }
  );


  const data = await response
    .json()
    .catch(() => null);


  if (!response.ok) {

    /*
     * Do NOT expose raw backend,
     * Groq, Pydantic, or Django errors.
     */

    throw new Error(
      GENERIC_REVIEW_ERROR
    );
  }


  return data;
}


export async function getReview(
  id: number | string
): Promise<Review> {

  const response = await fetch(
    `${API_BASE_URL}${id}/`,
    {
      method: "GET",

      headers: {
        "Accept": "application/json",
      },
    }
  );


  if (!response.ok) {
    throw new Error(
      "Unable to load this code review."
    );
  }


  return response.json();
}


export async function getReviews(): Promise<Review[]> {

  const response = await fetch(
    API_BASE_URL,
    {
      method: "GET",

      headers: {
        "Accept": "application/json",
      },
    }
  );


  if (!response.ok) {
    throw new Error(
      "Unable to load your review history."
    );
  }


  return response.json();
}


export async function retryReview(
  id: number | string
): Promise<Review> {

  const response = await fetch(
    `${API_BASE_URL}${id}/retry/`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
    }
  );


  const data = await response
    .json()
    .catch(() => null);


  if (!response.ok) {
    throw new Error(
      GENERIC_REVIEW_ERROR
    );
  }


  return data;
}