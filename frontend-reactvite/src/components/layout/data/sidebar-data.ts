import {
  Construction,
  LayoutDashboard,
  Monitor,
  Bug,
  FileX,
  HelpCircle,
  Lock,
  Bell,
  Palette,
  ServerOff,
  Settings,
  Wrench,
  UserCog,
  UserX,
  Users,
  ShieldCheck,
  Briefcase,
  Building2,
  FileText,
  Search,
  CreditCard,
  Star,
  BarChart3,
  User,
  ShoppingBag,
  MessageCircle,
} from "lucide-react";
import { type SidebarData } from "../types";

export const sidebarData: SidebarData = {
  user: {
    name: "satnaing",
    email: "satnaingdev@gmail.com",
    avatar: "/avatars/shadcn.jpg",
  },
  teams: [
    {
      name: "Job Portal",
      logo: Briefcase,
      plan: "Professional",
    },
    {
      name: "Company Dashboard",
      logo: Building2,
      plan: "Enterprise",
    },
    {
      name: "Analytics Hub",
      logo: BarChart3,
      plan: "Premium",
    },
  ],
  navGroups: [
    {
      title: "Job Management",
      items: [
        {
          title: "Dashboard",
          url: "/",
          icon: LayoutDashboard,
        },
        {
          title: "Search Jobs",
          url: "/search",
          icon: Search,
        },
        {
          title: "Applications",
          url: "/apps",
          icon: FileText,
        },
        {
          title: "Orders",
          url: "/orders",
          icon: ShoppingBag,
        },
        {
          title: "Bids",
          url: "/bids",
          icon: Briefcase,
        },
      ],
    },
    {
      title: "Company & Services",
      items: [
        {
          title: "Service Providers",
          url: "/service-providers",
          icon: Building2,
        },
        {
          title: "Analytics",
          url: "/analytics",
          icon: BarChart3,
        },
        {
          title: "Reviews",
          url: "/reviews",
          icon: Star,
        },
        {
          title: "Payments",
          url: "/payments",
          icon: CreditCard,
        },
      ],
    },
    {
      title: "Communication",
      items: [
        {
          title: "Messages",
          url: "/chats",
          badge: "3",
          icon: MessageCircle,
        },
      ],
    },
    {
      title: "Pages",
      items: [
        {
          title: "Auth",
          icon: ShieldCheck,
          items: [
            {
              title: "Sign In",
              url: "/sign-in",
            },
            {
              title: "Sign In (2 Col)",
              url: "/sign-in-2",
            },
            {
              title: "Forgot Password",
              url: "/forgot-password",
            },
            {
              title: "OTP",
              url: "/otp",
            },
          ],
        },
        {
          title: "Errors",
          icon: Bug,
          items: [
            {
              title: "Unauthorized",
              url: "/errors/unauthorized",
              icon: Lock,
            },
            {
              title: "Forbidden",
              url: "/errors/forbidden",
              icon: UserX,
            },
            {
              title: "Not Found",
              url: "/errors/not-found",
              icon: FileX,
            },
            {
              title: "Internal Server Error",
              url: "/errors/internal-server-error",
              icon: ServerOff,
            },
            {
              title: "Maintenance Error",
              url: "/errors/maintenance-error",
              icon: Construction,
            },
          ],
        },
      ],
    },
    {
      title: "Profile & Settings",
      items: [
        {
          title: "Settings",
          icon: Settings,
          items: [
            {
              title: "Profile",
              url: "/settings/profile",
              icon: User,
            },
            {
              title: "Client Profile",
              url: "/settings/client-profile",
              icon: UserCog,
            },
            {
              title: "Service Provider",
              url: "/settings/service-provider",
              icon: Building2,
            },
            {
              title: "Appearance",
              url: "/settings/appearance",
              icon: Palette,
            },
            {
              title: "Notifications",
              url: "/settings/notifications",
              icon: Bell,
            },
            {
              title: "Display",
              url: "/settings/display",
              icon: Monitor,
            },
          ],
        },
        {
          title: "Help Center",
          url: "/help-center",
          icon: HelpCircle,
        },
      ],
    },
  ],
};
