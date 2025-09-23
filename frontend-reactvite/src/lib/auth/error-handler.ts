import { FirebaseError } from "firebase/app";

interface AuthError {
  code: string;
  message: string;
  userMessage: string;
}

/**
 * Maps Firebase authentication error codes to user-friendly messages
 * with i18next translation keys
 */
const getFirebaseErrorMessage = (errorCode: string): AuthError => {
  const errorMap: Record<string, AuthError> = {
    // Essential Firebase Auth Errors only
    "auth/invalid-email": {
      code: "auth/invalid-email",
      message: "The email address is badly formatted.",
      userMessage: "validation:auth.error.invalid_email",
    },
    "auth/user-not-found": {
      code: "auth/user-not-found",
      message: "There is no user record corresponding to this identifier.",
      userMessage: "validation:auth.error.user_not_found",
    },
    "auth/wrong-password": {
      code: "auth/wrong-password",
      message: "The password is invalid or the user does not have a password.",
      userMessage: "validation:auth.error.wrong_password",
    },
    "auth/invalid-credential": {
      code: "auth/invalid-credential",
      message: "The credential is invalid or has expired.",
      userMessage: "validation:auth.error.invalid_credential",
    },
    "auth/invalid-login-credentials": {
      code: "auth/invalid-login-credentials",
      message: "Invalid login credentials provided.",
      userMessage: "validation:auth.error.invalid_login_credentials",
    },
    "auth/email-already-in-use": {
      code: "auth/email-already-in-use",
      message: "The email address is already in use by another account.",
      userMessage: "validation:auth.error.email_already_in_use",
    },
    "auth/weak-password": {
      code: "auth/weak-password",
      message: "The password is too weak.",
      userMessage: "validation:auth.error.weak_password",
    },
    "auth/too-many-requests": {
      code: "auth/too-many-requests",
      message: "Too many requests. Try again later.",
      userMessage: "validation:auth.error.too_many_requests",
    },
    "auth/network-request-failed": {
      code: "auth/network-request-failed",
      message: "Network error. Please check your connection.",
      userMessage: "validation:auth.error.network_error",
    },
    "auth/popup-blocked": {
      code: "auth/popup-blocked",
      message: "Sign-in popup was blocked by the browser.",
      userMessage: "validation:auth.error.popup_blocked",
    },
  };

  // Return the mapped error or a default error
  return (
    errorMap[errorCode] || {
      code: errorCode,
      message: "An unknown error occurred.",
      userMessage: "auth.error.unknown",
    }
  );
};

/**
 * Gets user-friendly error message for display
 */
export const getUserFriendlyErrorMessage = (error: any): AuthError => {
  if(error instanceof Object) {
    const _typedError = error as FirebaseError;
    const authError = getFirebaseErrorMessage(_typedError.code);
    return authError;
  }
  return {
    message: "Unknown error",
    code: "Unknown error",
    userMessage: "Unknown error",
  };
};
