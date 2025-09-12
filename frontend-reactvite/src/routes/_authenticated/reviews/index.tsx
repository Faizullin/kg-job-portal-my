import { createFileRoute } from "@tanstack/react-router";
import { ReviewsList } from "@/features/reviews/reviews-list";

export const Route = createFileRoute("/_authenticated/reviews/")({
  component: ReviewsPage,
});

function ReviewsPage() {
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Reviews</h2>
      </div>
      <ReviewsList />
    </div>
  );
}