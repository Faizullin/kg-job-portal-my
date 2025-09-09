import { useNavigate, useLocation } from "@tanstack/react-router";
import { AuthClient } from "@/lib/auth/auth-client";
import { ConfirmDialog } from "@/components/confirm-dialog";

interface SignOutDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SignOutDialog({ open, onOpenChange }: SignOutDialogProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleSignOut = async () => {
    try {
      const result = await AuthClient.signOut();
      
      if (result.success) {
        // Preserve current location for redirect after sign-in
        const currentPath = location.href;
        navigate({
          to: "/sign-in",
          search: { redirect: currentPath },
          replace: true,
        });
      } else {
        console.error("Sign out error:", result.error);
        // Still navigate to sign-in even if logout fails
        navigate({
          to: "/sign-in",
          replace: true,
        });
      }
    } catch (error) {
      console.error("Sign out error:", error);
      // Still navigate to sign-in even if logout fails
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
