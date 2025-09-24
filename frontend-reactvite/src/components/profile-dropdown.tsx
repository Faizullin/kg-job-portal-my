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
import { useAuthStore } from "@/stores/auth-store";
import { Link } from "@tanstack/react-router";
import { useMemo } from "react";
import { User, Briefcase } from "lucide-react";

export function ProfileDropdown() {
  const control = useDialogControl();
  const { auth } = useAuthStore();

  // Memoize user data to prevent unnecessary re-computations
  const user = useMemo(() => {
    const backendUser = auth.user;  

    return backendUser
      ? {
        name: backendUser.username || backendUser.email.split("@")[0] || "User",
        email: backendUser.email,
        avatar: backendUser.photo_url || "/avatars/default.jpg",
        initials: (backendUser.username || backendUser.email.split("@")[0] || "U").substring(0, 2).toUpperCase(),
      }
      : {
        name: "User",
        email: "user@example.com",
        avatar: "/avatars/default.jpg",
        initials: "U",
      };
  }, [auth.user]); 

  // Profile switching logic
  const handleProfileToggle = () => {
    if (auth.currentProfile === 'client') {
      auth.setCurrentProfile('service_provider');
    } else if (auth.currentProfile === 'service_provider') {
      auth.setCurrentProfile('client');
    } else {
      // If no profile is selected, default to client if available, otherwise service provider
      auth.setCurrentProfile(hasClientGroup ? 'client' : 'service_provider');
    }
  };

  const getCurrentProfileLabel = () => {
    switch (auth.currentProfile) {
      case 'client':
        return 'Client';
      case 'service_provider':
        return 'Service Provider';
      default:
        return 'Select Profile';
    }
  };

  const getButtonText = () => {
    switch (auth.currentProfile) {
      case 'client':
        return 'Switch to Service Provider';
      case 'service_provider':
        return 'Switch to Client';
      default:
        return hasClientGroup ? 'Activate Client' : 'Activate Service Provider';
    }
  };

  const getButtonIcon = () => {
    switch (auth.currentProfile) {
      case 'client':
        return <Briefcase className="h-4 w-4 mr-2" />;
      case 'service_provider':
        return <User className="h-4 w-4 mr-2" />;
      default:
        return hasClientGroup ? <User className="h-4 w-4 mr-2" /> : <Briefcase className="h-4 w-4 mr-2" />;
    }
  };

  // Check user groups for profile availability
  const hasClientGroup = useMemo(() => {
    if (!auth.user?.groups) return false;
    return auth.user.groups.includes('client') || auth.user.groups.includes('Client');
  }, [auth.user?.groups]);

  const hasServiceProviderGroup = useMemo(() => {
    if (!auth.user?.groups) return false;
    return auth.user.groups.includes('service_provider') || 
           auth.user.groups.includes('Service Provider') ||
           auth.user.groups.includes('serviceprovider');
  }, [auth.user?.groups]);

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
          
          {/* Profile Switching Section */}
          <DropdownMenuGroup>
            <DropdownMenuLabel className="text-xs text-muted-foreground">
              Current Profile: {getCurrentProfileLabel()}
            </DropdownMenuLabel>
            
            <div className="px-2 py-1.5">
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={handleProfileToggle}
                disabled={!hasClientGroup && !hasServiceProviderGroup}
              >
                {getButtonIcon()}
                {getButtonText()}
              </Button>
            </div>
          </DropdownMenuGroup>
          
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
