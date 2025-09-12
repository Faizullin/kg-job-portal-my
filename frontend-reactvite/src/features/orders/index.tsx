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
import { Input } from "@/components/ui/input";
import { useDialogControl } from "@/hooks/use-dialog-control";
import type { Order } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  DollarSign,
  Edit,
  Eye,
  Loader2,
  MoreHorizontal,
  Plus,
  Search as SearchIcon,
  Tag,
} from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { OrderCreateEditDialog, type OrderFormData } from "./components/order-create-edit-dialog";


export function Orders() {
  const [searchQuery, setSearchQuery] = useState("");

  // Dialog controls
  const orderDialog = useDialogControl<OrderFormData>();

  // Load orders with TanStack Query
  const ordersQuery = useQuery({
    queryKey: ['orders', searchQuery],
    queryFn: () => myApi.v1OrdersList({
      search: searchQuery || undefined,
      page: 1,
      pageSize: 10,
    }).then(r => r.data),
    staleTime: 5 * 60 * 1000,
  });

  const orders = ordersQuery.data?.results || [];

  // Dialog handlers
  const handleCreateOrder = useCallback(() => {
    orderDialog.show();
  }, [orderDialog]);

  const handleEditOrder = useCallback((order: Order) => {
    orderDialog.show({
      id: order.id,
      title: order.title,
      description: order.description,
      service_category: "", // Will be populated by the dialog based on subcategory
      service_subcategory: "", // Will be populated by the dialog based on subcategory ID
      location: order.location,
      city: order.city,
      state: order.state,
      country: order.country,
      postal_code: order.postal_code,
      service_date: order.service_date || "",
      service_time: order.service_time || "",
      urgency: order.urgency || "medium",
      budget_min: order.budget_min ? Number(order.budget_min) : 0,
      budget_max: order.budget_max ? Number(order.budget_max) : 0,
      special_requirements: order.special_requirements || ""
    });
  }, [orderDialog]);

  const getStatusColor = useCallback((status: string) => {
    switch (status) {
      case 'published': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }, []);

  const totalCount = orders.length;

  // Define columns with useMemo
  const columns = useMemo<ColumnDef<Order, any>[]>(() => [
    {
      accessorKey: "title",
      header: "Title",
      cell: ({ row }) => (
        <div className="max-w-[200px]">
          <div className="font-medium truncate">{row.getValue("title")}</div>
          <div className="text-sm text-muted-foreground truncate">
            {row.original.description}
          </div>
        </div>
      ),
      meta: {
        variant: "text",
        placeholder: "Search orders...",
        label: "Search",
        className: ""
      }
    },
    {
      accessorKey: "client_name",
      header: "Client",
      cell: ({ row }) => (
        <div className="flex items-center gap-1">
          <Tag className="h-3 w-3" />
          <span className="text-sm">{row.getValue("client_name")}</span>
        </div>
      ),
      meta: {
        variant: "text",
        label: "Client",
        className: ""
      }
    },
    {
      accessorKey: "status_display",
      header: "Status",
      cell: ({ row }) => (
        <Badge className={getStatusColor(row.getValue("status_display"))}>
          {String(row.getValue("status_display")).replace('_', ' ').toUpperCase()}
        </Badge>
      ),
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
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link to="/orders/$orderId" params={{ orderId: row.original.id.toString() }} className="flex items-center gap-2">
                <Eye className="h-4 w-4" />
                View Details
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleEditOrder(row.original)} className="flex items-center gap-2">
              <Edit className="h-4 w-4" />
              Edit
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ], [getStatusColor, handleEditOrder]);

  const { table } = useDataTable({
    data: orders,
    columns,
    pageCount: Math.ceil(totalCount / 10),
  });

  // Loading state
  if (ordersQuery.isLoading) {
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
          <div className="flex items-center justify-center h-64">
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Loading orders...</span>
            </div>
          </div>
        </Main>
      </>
    );
  }

  // Error state
  if (ordersQuery.error) {
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
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p className="text-destructive">Failed to load orders</p>
              <p className="text-sm text-muted-foreground mt-1">
                {ordersQuery.error instanceof Error ? ordersQuery.error.message : "An error occurred"}
              </p>
            </div>
          </div>
        </Main>
      </>
    );
  }

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
        <div className="mb-2 flex flex-wrap items-center justify-between space-y-2 gap-x-4">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Orders</h2>
            <p className="text-muted-foreground">
              Manage and track your service orders
            </p>
          </div>
        </div>
        <div className="-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-y-0 lg:space-x-12">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">All Orders</h3>
                <p className="text-sm text-muted-foreground">
                  {totalCount} order{totalCount !== 1 ? 's' : ''} found
                </p>
              </div>
              <Button onClick={handleCreateOrder} className="gap-2">
                <Plus className="h-4 w-4" />
                Create New Order
              </Button>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="relative flex-1 max-w-sm">
                  <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search orders..."
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    className="pl-8 h-8"
                  />
                </div>
              </div>
              <DataTable table={table}>
                <DataTableToolbar table={table} />
              </DataTable>
            </div>

            {/* Dialogs */}
            <OrderCreateEditDialog
              control={orderDialog}
            />
          </div>
        </div>
      </Main>
    </>
  );
}
