import { createFileRoute } from "@tanstack/react-router";
import { SplashScreen } from "@/features/auth/splash-screen";

export const Route = createFileRoute("/(auth)/splash")({
  component: SplashScreen,
});