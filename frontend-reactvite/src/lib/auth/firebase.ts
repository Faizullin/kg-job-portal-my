import { getApp, getApps, initializeApp } from "firebase/app";
import {
  createUserWithEmailAndPassword,
  getAuth,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  type User,
} from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FB_API_KEY,
  authDomain: import.meta.env.VITE_FB_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FB_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FB_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FB_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FB_APP_ID,
};

// Initialize Firebase
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const firebaseAuth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export const getFirebaseAuth = () => firebaseAuth;

// Auth functions
export const signInWithEmail = (email: string, password: string) =>
  signInWithEmailAndPassword(firebaseAuth, email, password);

export const signUpWithEmail = (email: string, password: string) =>
  createUserWithEmailAndPassword(firebaseAuth, email, password);

export const signInWithGoogle = () =>
  signInWithPopup(firebaseAuth, googleProvider);

export const logout = () => signOut(firebaseAuth);

export const onAuthStateChange = (callback: (user: User | null) => void) =>
  onAuthStateChanged(firebaseAuth, callback);

export { app, firebaseAuth };
