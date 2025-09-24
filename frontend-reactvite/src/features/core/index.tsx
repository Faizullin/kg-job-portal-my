import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Building2, 
  Settings, 
  MapPin, 
  Layers, 
  HelpCircle,
  BarChart3,
  Users,
  Shield,
  ShoppingBag,
  Star,
  MessageCircle,
  CreditCard
} from "lucide-react";
import { Link } from "@tanstack/react-router";

export function AdminDashboard() {
  const coreFeatures = [
    {
      title: "Categories",
      description: "Manage service categories and their configurations",
      icon: Building2,
      href: "/core/categories",
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "Subcategories", 
      description: "Manage specific services within categories",
      icon: Layers,
      href: "/core/subcategories",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "Areas",
      description: "Manage geographic service areas and pricing",
      icon: MapPin,
      href: "/core/areas", 
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      title: "Settings",
      description: "Configure system-wide settings and parameters",
      icon: Settings,
      href: "/core/settings",
      color: "text-orange-600", 
      bgColor: "bg-orange-50",
    },
    {
      title: "FAQ",
      description: "Manage frequently asked questions and help content",
      icon: HelpCircle,
      href: "/core/faq",
      color: "text-pink-600",
      bgColor: "bg-pink-50",
    },
  ];

  const quickActions = [
    {
      title: "View Orders",
      description: "Monitor all orders and their status",
      icon: ShoppingBag,
      href: "/orders",
      color: "text-emerald-600",
      bgColor: "bg-emerald-50",
    },
    {
      title: "Manage Reviews",
      description: "Review and moderate user reviews",
      icon: Star,
      href: "/reviews",
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
    },
    {
      title: "View Messages",
      description: "Monitor customer support messages",
      icon: MessageCircle,
      href: "/chats",
      color: "text-indigo-600",
      bgColor: "bg-indigo-50",
    },
    {
      title: "Payment Overview",
      description: "Track payments and transactions",
      icon: CreditCard,
      href: "/payments",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
  ];

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Core Management</h1>
        <p className="text-gray-600 mt-2">
          Manage system configuration, services, and monitor platform activity
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Card key={action.href} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="pb-3">
                  <div className={`w-10 h-10 ${action.bgColor} rounded-lg flex items-center justify-center mb-3`}>
                    <Icon className={`w-5 h-5 ${action.color}`} />
                  </div>
                  <CardTitle className="text-lg">{action.title}</CardTitle>
                  <CardDescription className="text-sm">{action.description}</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <Button asChild variant="outline" className="w-full">
                    <Link to={action.href}>
                      View
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Core Management */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Core Management</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {coreFeatures.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.href} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className={`w-12 h-12 ${feature.bgColor} rounded-lg flex items-center justify-center mb-4`}>
                    <Icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button asChild className="w-full">
                    <Link to={feature.href}>
                      Manage {feature.title}
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,234</div>
              <p className="text-xs text-muted-foreground">
                +12% from last month
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Orders</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">456</div>
              <p className="text-xs text-muted-foreground">
                +8% from last month
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Service Providers</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">89</div>
              <p className="text-xs text-muted-foreground">
                +5% from last month
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">99.9%</div>
              <p className="text-xs text-muted-foreground">
                All systems operational
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
