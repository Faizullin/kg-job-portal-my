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
import type { Job } from "@/lib/api/axios-client";
import { UrgencyEnum } from "@/lib/api/axios-client";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  DollarSign,
  Edit,
  Eye,
  MoreHorizontal,
  Plus,
  Search as SearchIcon,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { JobCreateEditDialog, type JobFormData } from "./components/job-create-edit-dialog";


export function Jobs() {
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
        <JobsTable />
      </Main>
    </>
  );
}

const loadJobsQueryKey = 'jobs';

const JobsTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<Job>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const jobDialog = useDialogControl<JobFormData>();

  const queryClient = useQueryClient();

  const loadJobsQuery = useQuery({
    queryKey: [loadJobsQueryKey, debouncedSearchQuery],
    queryFn: async () => {
      const response = await myApi.v1JobsList({
        search: debouncedSearchQuery || undefined,
        page: 1,
        pageSize: 10,
      });
      return response.data;
    },
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadJobsQuery.data) return;
    const parsed = loadJobsQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        (loadJobsQuery.data.count || 0) / 10,
      ),
    });
  }, [loadJobsQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleCreateJob = useCallback(() => {
    jobDialog.show(undefined);
  }, [jobDialog]);

  const handleEditJob = useCallback((job: Job) => {
    jobDialog.show({
      id: job.id,
      title: job.title,
      description: job.description,
      location: job.location,
      budget_min: job.budget_min || "",
      budget_max: job.budget_max || "",
      service_date: job.service_date || "",
      service_time: job.service_time || "",
      urgency: job.urgency || UrgencyEnum.medium,
      service_category: undefined as any,
      service_subcategory: undefined as any,
      country: undefined as any,
      city: undefined as any,
    });
  }, [jobDialog]);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1JobsDestroy({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadJobsQueryKey] });
      toast.success("Job deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete job");
    },
  });
  const deleteMutationMutateAsync = deleteMutation.mutateAsync;
  const handleDeleteJob = useCallback((job: Job) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Job",
        desc: `Are you sure you want to delete "${job.title}"? This action cannot be undone.`,
      }
    }).then((response) => {
      if (response.reason === "confirm") {
        deleteMutationMutateAsync(job.id);
      }
    })
  }, [deleteMutationMutateAsync]);

  const getStatusColor = useCallback((status: string) => {
    switch (status) {
      case 'published': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }, []);

  const columns = useMemo<ColumnDef<Job, any>[]>(() => [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <a className="font-mono text-sm" href="#" onClick={(e) => {
          e.preventDefault();
          handleEditJob(row.original);
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
      header: "Job",
      cell: ({ row }) => (
        <div className="max-w-[300px]">
          <div className="font-medium truncate">{row.getValue("title")}</div>
          <div className="text-sm text-muted-foreground truncate">
            {row.original.description?.substring(0, 100)}...
          </div>
          {row.original.employer?.user?.first_name && (
            <div className="text-xs text-blue-600 truncate">
              Client: {row.original.employer.user.first_name}
            </div>
          )}
        </div>
      ),
      meta: {
        variant: "text",
        placeholder: "Search jobs...",
        label: "Search",
        className: ""
      }
    },
    {
      accessorKey: "status_display",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue("status_display") as string;
        return (
          <Badge className={getStatusColor(status)}>
            {status?.replace('_', ' ').toUpperCase() || 'Unknown'}
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Status",
        options: [
          { label: "Published", value: "published" },
          { label: "In Progress", value: "in_progress" },
          { label: "Completed", value: "completed" },
          { label: "Cancelled", value: "cancelled" },
        ],
        className: ""
      }
    },
    {
      accessorKey: "budget_min",
      header: "Budget",
      cell: ({ row }) => {
        const budgetMin = row.getValue("budget_min") as string;
        const budgetMax = row.original.budget_max as string;
        const displayBudget = budgetMin && budgetMax ?
          `${budgetMin} - ${budgetMax}` :
          budgetMin || budgetMax || "Not set";

        return (
          <div className="flex items-center gap-1">
            <DollarSign className="h-3 w-3" />
            <span className="font-medium">{displayBudget}</span>
          </div>
        );
      },
      meta: {
        variant: "number",
        label: "Budget",
        unit: "$",
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
        const job = row.original;
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
                <Link to="/jobs/$jobId" params={{ jobId: job.id.toString() }} className="flex items-center gap-2">
                  <Eye className="h-4 w-4" />
                  View Details
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEditJob(job)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start text-red-600" onClick={() => handleDeleteJob(job)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getStatusColor, handleEditJob, handleDeleteJob]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadJobsQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadJobsQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading jobs</p>
        <Button onClick={() => loadJobsQuery.refetch()} className="mt-2">
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
            <h3 className="text-lg font-semibold">Jobs</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} job{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
          <Button onClick={handleCreateJob} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Job
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search jobs..."
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

      <JobCreateEditDialog
        control={jobDialog}
      />
    </div>
  );
}
