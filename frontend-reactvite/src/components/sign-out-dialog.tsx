import { ConfirmDialog } from "@/components/confirm-dialog";
import { useDialogControl } from "@/hooks/use-dialog-control";
import { AuthClient } from "@/lib/auth/auth-client";
import { useLocation, useNavigate } from "@tanstack/react-router";

interface SignOutDialogProps {
  control: ReturnType<typeof useDialogControl<any>>;
  onCancel?: () => void;
}

export function SignOutDialog({ control, onCancel }: SignOutDialogProps) {
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

  const handleCancel = () => {
    control.hide();
    onCancel?.();
  };

  return (
    <ConfirmDialog
      control={control}
      onConfirm={handleSignOut}
      onCancel={handleCancel}
      title="Sign out"
      desc="Are you sure you want to sign out? You will need to sign in again to access your account."
      confirmText="Sign out"
      className="sm:max-w-sm"
    />
  );
}


