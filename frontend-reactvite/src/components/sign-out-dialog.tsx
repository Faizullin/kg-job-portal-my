import { useNavigate, useLocation } from "@tanstack/react-router";
import { useAuthStore } from "@/stores/auth-store";
import { logout } from "@/lib/auth/firebase";
import { ConfirmDialog } from "@/components/confirm-dialog";

interface SignOutDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SignOutDialog({ open, onOpenChange }: SignOutDialogProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { auth } = useAuthStore();

  const handleSignOut = async () => {
    try {
      await logout();
      auth.reset();
      // Preserve current location for redirect after sign-in
      const currentPath = location.href;
      navigate({
        to: "/sign-in",
        search: { redirect: currentPath },
        replace: true,
      });
    } catch (error) {
      console.error("Sign out error:", error);
      // Still reset local state even if Firebase logout fails
      auth.reset();
      navigate({
        to: "/sign-in",
        replace: true,
      });
    }
  };

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Sign out"
      desc="Are you sure you want to sign out? You will need to sign in again to access your account."
      confirmText="Sign out"
      handleConfirm={handleSignOut}
      className="sm:max-w-sm"
    />
  );
}
