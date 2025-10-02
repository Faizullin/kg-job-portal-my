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
  Loader2,
  MoreHorizontal,
  Plus,
  Trash2,
} from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";

// Define resume interface based on API structure
interface Resume {
  id: number;
  title: string;
  summary: string;
  experience_years: number;
  education: string;
  certifications: string;
  created_at: string;
  updated_at: string;
}

export function ResumePage() {
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
        <ResumeTable />
      </Main>
    </>
  );
}

const RESUME_PAGE_QUERY_KEY = 'resume-page';

const ResumeTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingResume, setEditingResume] = useState<Resume | null>(null);
  
  const queryClient = useQueryClient();

  const loadResumeListQuery = useQuery({
    queryKey: [RESUME_PAGE_QUERY_KEY, searchQuery],
    queryFn: async () => {
      // Using a mock API call since the actual API endpoint needs to be determined
      // This will be replaced with the actual API call once the endpoint is identified
      const response = await fetch('/api/v1/users/my-resume/', {
        method: 'GET',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch resume');
      }
      return await response.json();
    },
    staleTime: 5 * 60 * 1000,
  });

  const resumes = useMemo(() => {
    // Mock data for now - replace with actual API response
    return [
      {
        id: 1,
        title: "Senior Software Engineer Resume",
        summary: "Experienced software engineer with 5+ years in full-stack development",
        experience_years: 5,
        education: "Bachelor's in Computer Science",
        certifications: "AWS Certified Developer, Google Cloud Professional",
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-20T14:30:00Z",
      },
      {
        id: 2,
        title: "Frontend Developer Resume",
        summary: "Specialized in React, Vue.js, and modern frontend technologies",
        experience_years: 3,
        education: "Bachelor's in Information Technology",
        certifications: "React Developer Certification",
        created_at: "2024-01-10T09:00:00Z",
        updated_at: "2024-01-18T16:45:00Z",
      }
    ] as Resume[];
  }, []);

  const createResumeMutation = useMutation({
    mutationFn: async (resumeData: Partial<Resume>) => {
      // Mock API call - replace with actual API call
      const response = await fetch('/api/v1/users/my-resume/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(resumeData),
      });
      if (!response.ok) {
        throw new Error('Failed to create resume');
      }
      return await response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [RESUME_PAGE_QUERY_KEY] });
      toast.success("Resume created successfully!");
      setShowCreateDialog(false);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to create resume");
    },
  });

  const updateResumeMutation = useMutation({
    mutationFn: async ({ id, ...resumeData }: Partial<Resume> & { id: number }) => {
      // Mock API call - replace with actual API call
      const response = await fetch(`/api/v1/users/my-resume/${id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(resumeData),
      });
      if (!response.ok) {
        throw new Error('Failed to update resume');
      }
      return await response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [RESUME_PAGE_QUERY_KEY] });
      toast.success("Resume updated successfully!");
      setEditingResume(null);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to update resume");
    },
  });

  const deleteResumeMutation = useMutation({
    mutationFn: async (id: number) => {
      // Mock API call - replace with actual API call
      const response = await fetch(`/api/v1/users/my-resume/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to delete resume');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [RESUME_PAGE_QUERY_KEY] });
      toast.success("Resume deleted successfully!");
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to delete resume");
    },
  });

  const handleCreateResume = useCallback(() => {
    setEditingResume(null);
    setShowCreateDialog(true);
  }, []);

  const handleEditResume = useCallback((resume: Resume) => {
    setEditingResume(resume);
    setShowCreateDialog(true);
  }, []);

  const handleDeleteResume = useCallback((resume: Resume) => {
    if (window.confirm(`Are you sure you want to delete "${resume.title}"?`)) {
      deleteResumeMutation.mutate(resume.id);
    }
  }, [deleteResumeMutation]);

  const getExperienceColor = useCallback((years: number) => {
    if (years >= 5) return 'bg-green-100 text-green-800';
    if (years >= 3) return 'bg-blue-100 text-blue-800';
    if (years >= 1) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  }, []);

  const totalCount = useMemo(() => resumes.length, [resumes]);

  const columns = useMemo<ColumnDef<Resume>[]>(() => [
    {
      accessorKey: "title",
      header: "Title",
      cell: ({ row }) => (
        <div className="max-w-[250px]">
          <div className="font-medium truncate">{row.getValue("title")}</div>
          <div className="text-sm text-muted-foreground truncate">
            {row.original.summary}
          </div>
        </div>
      ),
      meta: {
        variant: "text",
        placeholder: "Search resumes...",
        label: "Search",
        className: ""
      }
    },
    {
      accessorKey: "experience_years",
      header: "Experience",
      cell: ({ row }) => {
        const years = row.getValue("experience_years") as number;
        return (
          <Badge className={getExperienceColor(years)}>
            {years} years
          </Badge>
        );
      },
      meta: {
        variant: "number",
        label: "Experience",
        unit: "years",
        className: ""
      }
    },
    {
      accessorKey: "education",
      header: "Education",
      cell: ({ row }) => (
        <div className="max-w-[200px] truncate text-sm">
          {row.getValue("education")}
        </div>
      ),
      meta: {
        variant: "text",
        label: "Education",
        className: ""
      }
    },
    {
      accessorKey: "certifications",
      header: "Certifications",
      cell: ({ row }) => (
        <div className="max-w-[200px] truncate text-sm">
          {row.getValue("certifications")}
        </div>
      ),
      meta: {
        variant: "text",
        label: "Certifications",
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
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleEditResume(row.original)}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleDeleteResume(row.original)}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ], [getExperienceColor, handleEditResume, handleDeleteResume]);

  const { table } = useDataTable({
    data: resumes,
    columns,
    pageCount: Math.ceil(totalCount / 10),
  });

  if (loadResumeListQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (loadResumeListQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Error loading resumes: {loadResumeListQuery.error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Resume Management</h2>
          <p className="text-muted-foreground">
            Manage your professional resumes and experience details.
          </p>
        </div>
        <Button onClick={handleCreateResume}>
          <Plus className="mr-2 h-4 w-4" />
          Add Resume
        </Button>
      </div>

      <DataTable table={table}>
        <DataTableToolbar table={table} />
      </DataTable>

      {/* TODO: Add ResumeCreateEditDialog component */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {editingResume ? 'Edit Resume' : 'Create Resume'}
            </h3>
            <p className="text-muted-foreground">
              Resume creation/edit dialog will be implemented here.
            </p>
            <div className="flex justify-end space-x-2 mt-4">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button>
                {editingResume ? 'Update' : 'Create'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
