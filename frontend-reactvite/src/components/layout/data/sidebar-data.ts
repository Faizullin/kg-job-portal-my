import {
  BarChart3,
  Bell,
  Briefcase,
  Building2,
  FileText,
  HelpCircle,
  LayoutDashboard,
  MessageCircle,
  Monitor,
  Palette,
  Search,
  Settings,
  Shield,
  ShoppingBag,
  User,
  UserCog,
  Award,
  FolderOpen
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
          url: "/app/search",
          icon: Search,
        },
        {
          title: "Jobs",
          url: "/jobs",
          icon: ShoppingBag,
        },
      ],
    },
    // {
    //   title: "Company & Services",
    //   items: [
    //     {
    //       title: "Analytics",
    //       url: "/analytics",
    //       icon: BarChart3,
    //     },
    //     {
    //       title: "Reviews",
    //       url: "/reviews",
    //       icon: Star,
    //     },
    //     {
    //       title: "Payments",
    //       url: "/payments",
    //       icon: CreditCard,
    //     },
    //   ],
    // },
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
      title: "Subscribers",
      items: [
        {
          title: "Resume",
          url: "/subscribers/resumes",
          icon: FileText,
        },
        {
          title: "Skills",
          url: "/subscribers/skills",
          icon: Award,
        },
        {
          title: "Portfolio",
          url: "/subscribers/portfolio",
          icon: FolderOpen,
        },
      ],
    },
    {
      title: "Core Management",
      items: [
        {
          title: "Core",
          icon: Shield,
          items: [
            {
              title: "Dashboard",
              url: "/core",
            },
            {
              title: "Categories",
              url: "/core/service-categories",
            },
            {
              title: "Subcategories",
              url: "/core/service-subcategories",
            },
            {
              title: "Areas",
              url: "/core/service-areas",
            },
            {
              title: "Settings",
              url: "/core/settings",
            },
            {
              title: "FAQ",
              url: "/core/faq",
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
              title: "Master",
              url: "/settings/master",
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
