import { ConfigDrawer } from "@/components/config-drawer";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { useDataTable } from "@/components/data-table/use-data-table";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { Search } from "@/components/search";
import { ThemeSwitch } from "@/components/theme-switch";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  Edit,
  Eye,
  ExternalLink,
  Image,
  Loader2,
  MoreHorizontal,
  Plus,
  Trash2,
} from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";

// Define portfolio interface based on API structure
interface PortfolioItem {
  id: number;
  title: string;
  description: string;
  image_url?: string;
  project_url?: string;
  technologies: string[];
  category: string;
  client_name?: string;
  completion_date: string;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export function PortfolioPage() {
  return (
    <>
      <Header fixed>
        <Search />
        <div className="ms-auto flex items-center space-x-4">
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <PortfolioTable />
      </Main>
    </>
  );
}

const PORTFOLIO_PAGE_QUERY_KEY = 'portfolio-page';

const PortfolioTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingPortfolio, setEditingPortfolio] = useState<PortfolioItem | null>(null);
  
  const queryClient = useQueryClient();

  const loadPortfolioListQuery = useQuery({
    queryKey: [PORTFOLIO_PAGE_QUERY_KEY, searchQuery],
    queryFn: async () => {
      // Using a mock API call since the actual API endpoint needs to be determined
      // This will be replaced with the actual API call once the endpoint is identified
      const response = await fetch('/api/v1/users/my-portfolio/', {
        method: 'GET',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch portfolio items');
      }
      return await response.json();
    },
    staleTime: 5 * 60 * 1000,
  });

  const portfolioItems = useMemo(() => {
    // Mock data for now - replace with actual API response
    return [
      {
        id: 1,
        title: "E-commerce Website",
        description: "Full-stack e-commerce platform with React frontend and Node.js backend",
        image_url: "https://via.placeholder.com/300x200",
        project_url: "https://example-ecommerce.com",
        technologies: ["React", "Node.js", "MongoDB", "Stripe"],
        category: "Web Development",
        client_name: "TechCorp Inc.",
        completion_date: "2024-01-15",
        is_featured: true,
        created_at: "2024-01-10T10:00:00Z",
        updated_at: "2024-01-15T14:30:00Z",
      },
      {
        id: 2,
        title: "Mobile Banking App",
        description: "Cross-platform mobile banking application with secure authentication",
        image_url: "https://via.placeholder.com/300x200",
        project_url: "https://apps.apple.com/banking-app",
        technologies: ["React Native", "Firebase", "Redux", "JWT"],
        category: "Mobile Development",
        client_name: "FinanceBank",
        completion_date: "2023-12-20",
        is_featured: false,
        created_at: "2023-11-15T09:00:00Z",
        updated_at: "2023-12-20T16:45:00Z",
      },
      {
        id: 3,
        title: "AI Chatbot Integration",
        description: "Intelligent customer service chatbot with natural language processing",
        image_url: "https://via.placeholder.com/300x200",
        project_url: "https://chatbot-demo.com",
        technologies: ["Python", "OpenAI API", "FastAPI", "PostgreSQL"],
        category: "AI/ML",
        client_name: "CustomerService Co.",
        completion_date: "2024-02-01",
        is_featured: true,
        created_at: "2024-01-05T08:00:00Z",
        updated_at: "2024-02-01T12:00:00Z",
      }
    ] as PortfolioItem[];
  }, []);

  const createPortfolioMutation = useMutation({
    mutationFn: async (portfolioData: Partial<PortfolioItem>) => {
      // Mock API call - replace with actual API call
      const response = await fetch('/api/v1/users/my-portfolio/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(portfolioData),
      });
      if (!response.ok) {
        throw new Error('Failed to create portfolio item');
      }
      return await response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PORTFOLIO_PAGE_QUERY_KEY] });
      toast.success("Portfolio item created successfully!");
      setShowCreateDialog(false);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to create portfolio item");
    },
  });

  const updatePortfolioMutation = useMutation({
    mutationFn: async ({ id, ...portfolioData }: Partial<PortfolioItem> & { id: number }) => {
      // Mock API call - replace with actual API call
      const response = await fetch(`/api/v1/users/my-portfolio/${id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(portfolioData),
      });
      if (!response.ok) {
        throw new Error('Failed to update portfolio item');
      }
      return await response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PORTFOLIO_PAGE_QUERY_KEY] });
      toast.success("Portfolio item updated successfully!");
      setEditingPortfolio(null);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to update portfolio item");
    },
  });

  const deletePortfolioMutation = useMutation({
    mutationFn: async (id: number) => {
      // Mock API call - replace with actual API call
      const response = await fetch(`/api/v1/users/my-portfolio/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to delete portfolio item');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PORTFOLIO_PAGE_QUERY_KEY] });
      toast.success("Portfolio item deleted successfully!");
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to delete portfolio item");
    },
  });

  const handleCreatePortfolio = useCallback(() => {
    setEditingPortfolio(null);
    setShowCreateDialog(true);
  }, []);

  const handleEditPortfolio = useCallback((portfolio: PortfolioItem) => {
    setEditingPortfolio(portfolio);
    setShowCreateDialog(true);
  }, []);

  const handleDeletePortfolio = useCallback((portfolio: PortfolioItem) => {
    if (window.confirm(`Are you sure you want to delete "${portfolio.title}"?`)) {
      deletePortfolioMutation.mutate(portfolio.id);
    }
  }, [deletePortfolioMutation]);

  const getCategoryColor = useCallback((category: string) => {
    switch (category.toLowerCase()) {
      case 'web development': return 'bg-blue-100 text-blue-800';
      case 'mobile development': return 'bg-green-100 text-green-800';
      case 'ai/ml': return 'bg-purple-100 text-purple-800';
      case 'design': return 'bg-pink-100 text-pink-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }, []);

  const totalCount = useMemo(() => portfolioItems.length, [portfolioItems]);

  const columns = useMemo<ColumnDef<PortfolioItem>[]>(() => [
    {
      accessorKey: "title",
      header: "Project",
      cell: ({ row }) => (
        <div className="max-w-[300px]">
          <div className="font-medium truncate">{row.getValue("title")}</div>
          <div className="text-sm text-muted-foreground truncate">
            {row.original.description}
          </div>
          {row.original.client_name && (
            <div className="text-xs text-blue-600 truncate">
              Client: {row.original.client_name}
            </div>
          )}
        </div>
      ),
      meta: {
        variant: "text",
        placeholder: "Search projects...",
        label: "Search",
        className: ""
      }
    },
    {
      accessorKey: "image_url",
      header: "Preview",
      cell: ({ row }) => {
        const imageUrl = row.getValue("image_url") as string;
        return (
          <div className="w-16 h-12 rounded-md overflow-hidden bg-gray-100">
            {imageUrl ? (
              <img 
                src={imageUrl} 
                alt={row.original.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.nextElementSibling?.classList.remove('hidden');
                }}
              />
            ) : null}
            <div className={`w-full h-full flex items-center justify-center ${imageUrl ? 'hidden' : ''}`}>
              <Image className="h-6 w-6 text-gray-400" />
            </div>
          </div>
        );
      },
      meta: {
        variant: "text",
        label: "Image",
        className: ""
      }
    },
    {
      accessorKey: "category",
      header: "Category",
      cell: ({ row }) => {
        const category = row.getValue("category") as string;
        return (
          <Badge className={getCategoryColor(category)}>
            {category}
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Category",
        options: [
          { label: "Web Development", value: "Web Development" },
          { label: "Mobile Development", value: "Mobile Development" },
          { label: "AI/ML", value: "AI/ML" },
          { label: "Design", value: "Design" },
        ],
        className: ""
      }
    },
    {
      accessorKey: "technologies",
      header: "Technologies",
      cell: ({ row }) => {
        const technologies = row.getValue("technologies") as string[];
        return (
          <div className="flex flex-wrap gap-1 max-w-[200px]">
            {technologies.slice(0, 3).map((tech, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {tech}
              </Badge>
            ))}
            {technologies.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{technologies.length - 3}
              </Badge>
            )}
          </div>
        );
      },
      meta: {
        variant: "text",
        label: "Technologies",
        className: ""
      }
    },
    {
      accessorKey: "is_featured",
      header: "Featured",
      cell: ({ row }) => {
        const isFeatured = row.getValue("is_featured") as boolean;
        return (
          <Badge variant={isFeatured ? "default" : "secondary"}>
            {isFeatured ? "Featured" : "Regular"}
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Featured",
        options: [
          { label: "Featured", value: "true" },
          { label: "Regular", value: "false" },
        ],
        className: ""
      }
    },
    {
      accessorKey: "completion_date",
      header: "Completed",
      cell: ({ row }) => (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>{new Date(row.getValue("completion_date")).toLocaleDateString()}</span>
        </div>
      ),
      meta: {
        variant: "date",
        label: "Completion Date",
        className: ""
      }
    },
    {
      accessorKey: "project_url",
      header: "Links",
      cell: ({ row }) => {
        const projectUrl = row.getValue("project_url") as string;
        return (
          <div className="flex items-center gap-2">
            {projectUrl && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.open(projectUrl, '_blank')}
                className="h-8 w-8 p-0"
              >
                <ExternalLink className="h-3 w-3" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0"
            >
              <Eye className="h-3 w-3" />
            </Button>
          </div>
        );
      },
      meta: {
        variant: "text",
        label: "Actions",
        className: ""
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleEditPortfolio(row.original)}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleDeletePortfolio(row.original)}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ], [getCategoryColor, handleEditPortfolio, handleDeletePortfolio]);

  const { table } = useDataTable({
    data: portfolioItems,
    columns,
    pageCount: Math.ceil(totalCount / 10),
  });

  if (loadPortfolioListQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (loadPortfolioListQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Error loading portfolio: {loadPortfolioListQuery.error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Portfolio Management</h2>
          <p className="text-muted-foreground">
            Showcase your work portfolio and completed projects.
          </p>
        </div>
        <Button onClick={handleCreatePortfolio}>
          <Plus className="mr-2 h-4 w-4" />
          Add Project
        </Button>
      </div>

      <DataTable table={table}>
        <DataTableToolbar table={table} />
      </DataTable>

      {/* TODO: Add PortfolioCreateEditDialog component */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {editingPortfolio ? 'Edit Project' : 'Add Project'}
            </h3>
            <p className="text-muted-foreground">
              Portfolio creation/edit dialog will be implemented here.
            </p>
            <div className="flex justify-end space-x-2 mt-4">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button>
                {editingPortfolio ? 'Update' : 'Add'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
