import { ConfigDrawer } from "@/components/config-drawer";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { useDataTable } from "@/components/data-table/use-data-table";
import { DeleteConfirmNiceDialog } from "@/components/dialogs/delete-confirm-dialog";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import NiceModal from "@/components/nice-modal/modal-context";
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
import { Input } from "@/components/ui/input";
import { useDebounce } from "@/hooks/use-debounce";
import { useDialogControl } from "@/hooks/use-dialog-control";
import {
  type MasterSkillSkill,
  type PortfolioItem,
} from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  Edit,
  MoreHorizontal,
  Plus,
  SearchIcon,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { PortfolioCreateEditDialog, type PortfolioFormData } from "./components/portfolio-create-edit-dialog";

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
        <RenderTable />
      </Main>
    </>
  );
}

const loadPortfolioQueryKey = 'portfolio';

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<PortfolioItem>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const portfolioDialog = useDialogControl<PortfolioFormData>();

  const queryClient = useQueryClient();

  const loadPortfolioQuery = useQuery({
    queryKey: [loadPortfolioQueryKey, debouncedSearchQuery],
    queryFn: async () => {
      const response = await myApi.v1UsersMyPortfolioList({
        search: debouncedSearchQuery || undefined,
        page: 1,
        pageSize: 10,
      });
      return response.data;
    },
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadPortfolioQuery.data) return;
    const parsed = loadPortfolioQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        (loadPortfolioQuery.data.count || 0) / 10,
      ),
    });
  }, [loadPortfolioQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleCreatePortfolio = useCallback(() => {
    portfolioDialog.show(undefined);
  }, [portfolioDialog]);

  const handleEditPortfolio = useCallback((portfolio: PortfolioItem) => {
    portfolioDialog.show({
      id: portfolio.id,
      title: portfolio.title,
      description: portfolio.description,
      skill_used: portfolio.skill_used,
      is_featured: portfolio.is_featured || false,
    });
  }, [portfolioDialog]);

  const deleteMutation = useMutation({
    mutationFn: (id: string) => myApi.v1UsersMyPortfolioDestroy({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadPortfolioQueryKey] });
      toast.success("Portfolio item deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete portfolio item");
    },
  });
  const deleteMutationMutateAsync = deleteMutation.mutateAsync;
  const handleDeletePortfolio = useCallback((portfolio: PortfolioItem) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Portfolio Item",
        desc: `Are you sure you want to delete "${portfolio.title}"? This action cannot be undone.`,
      }
    }).then((response) => {
      if (response.reason === "confirm") {
        deleteMutationMutateAsync(portfolio.id.toString());
      }
    })
  }, [deleteMutationMutateAsync]);



  const getSkillColor = useCallback((skill: MasterSkillSkill) => {
    switch (skill.name?.toLowerCase()) {
      case 'web development': return 'bg-blue-100 text-blue-800';
      case 'mobile development': return 'bg-green-100 text-green-800';
      case 'ai/ml': return 'bg-purple-100 text-purple-800';
      case 'design': return 'bg-pink-100 text-pink-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }, []);


  const columns = useMemo<ColumnDef<PortfolioItem, any>[]>(() => [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <a className="font-mono text-sm" href="#" onClick={(e) => {
          e.preventDefault();
          handleEditPortfolio(row.original);
        }}>
          #{row.getValue("id")}
        </a>
      ),
      meta: {
        variant: "number",
        label: "ID",
        className: ""
      }
    },
    {
      accessorKey: "title",
      header: "Project",
      cell: ({ row }) => (
        <div className="max-w-[300px]">
          <div className="font-medium truncate">{row.getValue("title")}</div>
          <div className="text-sm text-muted-foreground truncate">
            {row.original.description?.substring(0, 100)}...
          </div>
          {row.original.skill_used?.name && (
            <div className="text-xs text-blue-600 truncate">
              Skill: {row.original.skill_used.name}
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
      accessorKey: "skill_used",
      header: "Skill",
      cell: ({ row }) => {
        const skill = row.getValue("skill_used") as MasterSkillSkill;
        return (
          <Badge className={getSkillColor(skill)}>
            {skill?.name || 'Unknown'}
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Skill",
        className: ""
      }
    },
    {
      accessorKey: "attachments",
      header: "Attachments",
      cell: ({ row }) => {
        const attachments = row.getValue("attachments") as Array<any>;
        return (
          <div className="flex items-center gap-1">
            <Badge variant="outline" className="text-xs">
              {attachments?.length || 0} files
            </Badge>
          </div>
        );
      },
      meta: {
        variant: "text",
        label: "Attachments",
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
      accessorKey: "created_at",
      header: "Created",
      cell: ({ row }) => (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>{new Date(row.getValue("created_at")).toLocaleDateString()}</span>
        </div>
      ),
      meta: {
        variant: "date",
        label: "Created Date",
        className: ""
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const portfolio = row.original;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEditPortfolio(portfolio)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start text-red-600" onClick={() => handleDeletePortfolio(portfolio)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getSkillColor, handleEditPortfolio, handleDeletePortfolio]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadPortfolioQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadPortfolioQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading portfolio</p>
        <Button onClick={() => loadPortfolioQuery.refetch()} className="mt-2">
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-y-0 lg:space-x-12">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Portfolio</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} project{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
          <Button onClick={handleCreatePortfolio} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Project
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="pl-8 h-8"
              />
            </div>
          </div>
        </div>
        <DataTable table={table}>
          <DataTableToolbar table={table} />
        </DataTable>
      </div>

      <PortfolioCreateEditDialog
        control={portfolioDialog}
      />
    </div>
  );
};

