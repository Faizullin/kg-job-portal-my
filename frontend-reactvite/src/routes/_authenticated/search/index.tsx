import { createFileRoute } from "@tanstack/react-router";
import { SearchPage } from "@/features/search/search-page";

export const Route = createFileRoute("/_authenticated/search/")({
  component: SearchPageComponent,
});

function SearchPageComponent() {
  return (
    <div className="flex-1 space-y-4 p-4 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Search</h2>
      </div>
      <SearchPage />
    </div>
  );
}