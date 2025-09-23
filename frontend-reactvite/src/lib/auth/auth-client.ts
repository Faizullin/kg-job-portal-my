import { useAuthStore } from "@/stores/auth-store";
import myApi from "../api/my-api";
import { getUserFriendlyErrorMessage } from "./error-handler";
import { getFirebaseAuth, getGoogleProvider } from "./firebase";
import {
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
} from "firebase/auth";

/**
 * AuthClient - Centralized authentication management
 * Provides static methods for all authentication operations
 */
export class AuthClient {
  /**
   * Sign in with email and password
   */
  static async signInWithEmailPassword(email: string, password: string) {
    try {
      const firebaseUser = await signInWithEmailAndPassword(getFirebaseAuth(), email, password);
      await this.authenticateWithBackend(firebaseUser.user);

      return {
        success: true,
        user: firebaseUser.user,
        message: `Welcome back, ${email}!`,
      };
    } catch (error: any) {
      return {
        success: false,
        error: getUserFriendlyErrorMessage(error),
      };
    }
  }

  /**
   * Sign up with email and password
   */
  static async signUpWithEmailPassword(email: string, password: string) {
    try {
      const firebaseUser = await createUserWithEmailAndPassword(getFirebaseAuth(), email, password);
      await this.authenticateWithBackend(firebaseUser.user);

      return {
        success: true,
        user: firebaseUser.user,
        message: `Account created successfully! Welcome, ${email}!`,
      };
    } catch (error: any) {
      return {
        success: false,
        error: getUserFriendlyErrorMessage(error),
      };
    }
  }

  /**
   * Sign in with Google
   */
  static async signInWithGoogle() {
    try {
      const result = await signInWithPopup(getFirebaseAuth(), getGoogleProvider());
      await this.authenticateWithBackend(result.user);

      return {
        success: true,
        user: result.user,
        message: `Welcome, ${result.user.email}!`,
      };
    } catch (error: any) {
      return {
        success: false,
        error: getUserFriendlyErrorMessage(error),
      };
    }
  }

  /**
   * Send password reset email
   */
  static async sendPasswordResetEmail(email: string) {
    try {
      await sendPasswordResetEmail(getFirebaseAuth(), email);
      
      return {
        success: true,
        message: `Password reset email sent to ${email}. Please check your inbox.`,
      };
    } catch (error: any) {
      return {
        success: false,
        error: getUserFriendlyErrorMessage(error),
      };
    }
  }

  /**
   * Sign out user
   */
  static async signOut() {
    try {
      await signOut(getFirebaseAuth());
      myApi.clearAuthData();
      const { auth } = useAuthStore.getState();
      auth.reset();

      return {
        success: true,
        message: "Signed out successfully",
      };
    } catch (error: any) {
      myApi.clearAuthData();
      const { auth } = useAuthStore.getState();
      auth.reset();

      return {
        success: false,
        error: error instanceof Error ? error.message : "Sign out failed",
      };
    }
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    const { auth } = useAuthStore.getState();
    return auth.isAuthenticated();
  }

  /**
   * Get current user from store
   */
  static getCurrentUser() {
    const { auth } = useAuthStore.getState();
    return auth.user;
  }

  /**
   * Get current Firebase user from store
   */
  static getCurrentFirebaseUser() {
    const { auth } = useAuthStore.getState();
    return auth.firebaseUser;
  }

  /**
   * Private method to handle backend authentication
   */
  private static async authenticateWithBackend(firebaseUser: any) {
    const { auth } = useAuthStore.getState();
    await auth.authenticateWithBackend(firebaseUser);
  }
}
