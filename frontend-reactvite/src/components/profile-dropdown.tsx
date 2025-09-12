import { SignOutDialog } from "@/components/sign-out-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useDialogControl } from "@/hooks/use-dialog-control";
import { AuthClient } from "@/lib/auth/auth-client";
import { Link } from "@tanstack/react-router";
import { useMemo } from "react";

export function ProfileDropdown() {
  const control = useDialogControl();

  // Memoize user data to prevent unnecessary re-computations
  const user = useMemo(() => {
    const backendUser = AuthClient.getCurrentUser();
    const firebaseUser = AuthClient.getCurrentFirebaseUser();

    return backendUser
      ? {
        name: backendUser.username || backendUser.email.split("@")[0] || "User",
        email: backendUser.email,
        avatar: firebaseUser?.photoURL || "/avatars/default.jpg",
        initials: (backendUser.username || backendUser.email.split("@")[0] || "U").substring(0, 2).toUpperCase(),
      }
      : {
        name: "User",
        email: "user@example.com",
        avatar: "/avatars/default.jpg",
        initials: "U",
      };
  }, []); // Empty dependency array since AuthClient methods are stable

  return (
    <>
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full">
            <Avatar className="h-8 w-8">
              <AvatarImage src={user.avatar} alt={user.name} />
              <AvatarFallback>{user.initials}</AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="end" forceMount>
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col gap-1.5">
              <p className="text-sm leading-none font-medium">{user.name}</p>
              <p className="text-muted-foreground text-xs leading-none">
                {user.email}
              </p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem asChild>
              <Link to="/settings/profile">
                Profile
                <DropdownMenuShortcut>⇧⌘P</DropdownMenuShortcut>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/settings/profile">
                Billing
                <DropdownMenuShortcut>⌘B</DropdownMenuShortcut>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/settings/profile">
                Settings
                <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem>New Team</DropdownMenuItem>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => control.show()}>
            Sign out
            <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <SignOutDialog control={control} />
    </>
  );
}
