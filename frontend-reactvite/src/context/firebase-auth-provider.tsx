import { useEffect } from "react";
import { onAuthStateChange } from "@/lib/auth/firebase";
import { useAuthStore } from "@/stores/auth-store";

export function FirebaseAuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { auth } = useAuthStore();

  useEffect(() => {
    const unsubscribe = onAuthStateChange(async (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in
        auth.setFirebaseUser(firebaseUser);

        // If we don't have backend user data, authenticate with backend
        if (!auth.user) {
          try {
            await auth.authenticateWithBackend(firebaseUser);
          } catch (error) {
            console.error("Failed to authenticate with backend:", error);
            // Still keep the Firebase user, but show error
          }
        }
      } else {
        // User is signed out
        auth.reset();
      }
    });

    return () => unsubscribe();
  }, [auth]);

  return <>{children}</>;
}
