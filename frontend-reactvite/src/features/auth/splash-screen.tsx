import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function SplashScreen() {
  const [showSplash, setShowSplash] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if this is the first launch
    const hasLaunchedBefore = localStorage.getItem("app_launched");
    
    if (!hasLaunchedBefore) {
      setShowSplash(true);
      localStorage.setItem("app_launched", "true");
    } else {
      // Skip splash screen for returning users
      navigate({ to: "/sign-in" });
    }
  }, [navigate]);

  const handleContinue = () => {
    setShowSplash(false);
    navigate({ to: "/sign-in" });
  };

  if (!showSplash) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="text-center text-white max-w-md mx-auto">
        {/* Logo */}
        <div className="mb-8">
          <div className="w-20 h-20 mx-auto mb-4 bg-white rounded-2xl flex items-center justify-center">
            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
              <div className="w-8 h-8 bg-white rounded grid grid-cols-2 gap-1">
                <div className="bg-purple-600 rounded-sm"></div>
                <div className="bg-purple-600 rounded-sm"></div>
                <div className="bg-purple-600 rounded-sm"></div>
                <div className="bg-purple-600 rounded-sm"></div>
              </div>
            </div>
          </div>
          <h1 className="text-3xl font-bold">Jobspot</h1>
        </div>

        {/* Illustration */}
        <div className="mb-8">
          <div className="w-64 h-48 mx-auto bg-white/10 rounded-2xl flex items-center justify-center backdrop-blur-sm">
            <div className="text-6xl">📱</div>
          </div>
        </div>

        {/* Content */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">
            Find Your <span className="text-orange-400">Dream Job</span> Here!
          </h2>
          <p className="text-gray-300 text-sm leading-relaxed">
            Explore all the most exciting job roles based on your interest and study major.
          </p>
        </div>

        {/* CTA Button */}
        <Button
          onClick={handleContinue}
          size="lg"
          className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-full"
        >
          Get Started
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
