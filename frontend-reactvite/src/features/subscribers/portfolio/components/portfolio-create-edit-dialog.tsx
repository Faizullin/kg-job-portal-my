import { AttachmentsView } from "@/components/attachments/attachments-view";
import ComboBox2 from "@/components/combobox";
import { FormDialog } from "@/components/dialogs/form-dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const portfolioFormSchema = z.object({
    id: z.number().optional(),
    title: z.string().min(1, "Title is required").max(200, "Title must be less than 200 characters"),
    description: z.string().max(1000, "Description must be less than 1000 characters").optional(),
    skill_used: z.object({
        id: z.number(),
        name: z.string(),
        description: z.string().optional(),
        category: z.number(),
        is_active: z.boolean().optional(),
    }).optional().refine((skill) => skill !== undefined, {
        message: "Skill is required",
    }),
    is_featured: z.boolean().optional(),
});

export type PortfolioFormData = z.infer<typeof portfolioFormSchema>;

const loadPortfolioDetailQueryKey = 'portfolio-detail';

interface PortfolioCreateEditDialogProps {
    control: ReturnType<typeof useDialogControl<PortfolioFormData>>;
    onSave?: (data: PortfolioFormData) => void;
    onCancel?: () => void;
}

export function PortfolioCreateEditDialog({
    control,
    onSave,
    onCancel,
}: PortfolioCreateEditDialogProps) {
    const queryClient = useQueryClient();
    const isEditMode = !!control.data?.id;

    const form = useForm<PortfolioFormData>({
        resolver: zodResolver(portfolioFormSchema),
        defaultValues: {
            title: "",
            description: "",
            skill_used: undefined,
            is_featured: false,
        },
    });

    const loadPortfolioDetailQuery = useQuery({
        queryKey: [loadPortfolioDetailQueryKey, control.data?.id],
        queryFn: () => myApi.v1UsersMyPortfolioRetrieve({ id: control.data!.id!.toString() }).then(r => r.data),
        enabled: isEditMode && !!control.data?.id,
    });

    const loadPortfolioAttachmentsQueryKey = ['portfolio-attachments', control.data?.id];
    const loadPortfolioAttachmentsQuery = useQuery({
        queryKey: loadPortfolioAttachmentsQueryKey,
        queryFn: () => myApi.v1UsersMyPortfolioAttachmentsList({
            portfolioId: control.data!.id!.toString()
        }).then(r => r.data.results || []),
        enabled: isEditMode && !!control.data?.id,
    });

    const searchSkills = useCallback(async (search: string, offset: number, size: number) => {
        try {
            const response = await myApi.v1UsersSkillsList({
                search: search || undefined,
                page: Math.floor(offset / size) + 1,
                pageSize: size,
                isActive: true, // Only get active skills
            });
            return response.data.results || [];
        } catch (error) {
            console.error("Error searching skills:", error);
            return [];
        }
    }, []);

    const createMutation = useMutation({
        mutationFn: (data: PortfolioFormData) => {
            const { id, ...createData } = data;
            return myApi.v1UsersMyPortfolioCreate({
                portfolioItemRequest: {
                    title: createData.title,
                    description: createData.description,
                    skill_used_id: createData.skill_used?.id,
                    is_featured: createData.is_featured || false,
                }
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['portfolio'] });
            toast.success("Portfolio item created successfully!");
            control.hide();
            onSave?.(form.getValues());
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || "Failed to create portfolio item");
        },
    });

    const updateMutation = useMutation({
        mutationFn: (data: PortfolioFormData) => {
            const { id, ...updateData } = data;
            return myApi.v1UsersMyPortfolioPartialUpdate({
                id: control.data!.id!.toString(),
                patchedPortfolioItemRequest: {
                    title: updateData.title,
                    description: updateData.description,
                    skill_used_id: updateData.skill_used?.id,
                    is_featured: updateData.is_featured,
                }
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['portfolio'] });
            queryClient.invalidateQueries({ queryKey: [loadPortfolioDetailQueryKey, control.data?.id] });
            toast.success("Portfolio item updated successfully!");
            control.hide();
            onSave?.(form.getValues());
        },
        onError: (error) => {
            if (error instanceof AxiosError) {
                toast.error(error.response?.data?.detail || "Failed to update portfolio item");
            } else {
                console.error("Error updating portfolio item:", error);
            }
        },
    });

    useEffect(() => {
        if (control.isVisible) {
            if (isEditMode && loadPortfolioDetailQuery.data) {
                form.reset({
                    id: loadPortfolioDetailQuery.data.id,
                    title: loadPortfolioDetailQuery.data.title,
                    description: loadPortfolioDetailQuery.data.description,
                    skill_used: loadPortfolioDetailQuery.data.skill_used,
                    is_featured: loadPortfolioDetailQuery.data.is_featured || false,
                });
            } else if (!isEditMode) {
                form.reset({
                    title: "",
                    description: "",
                    skill_used: undefined,
                    is_featured: false,
                });
            }
        }
    }, [control.isVisible, isEditMode, loadPortfolioDetailQuery.data, form]);

    const onSubmit = (data: PortfolioFormData) => {
        if (isEditMode) {
            updateMutation.mutate(data);
        } else {
            createMutation.mutate(data);
        }
    };

    const handleCancel = () => {
        form.reset({
            title: "",
            description: "",
            skill_used: undefined,
            is_featured: false,
        });
        control.hide();
        onCancel?.();
    };

    const isLoading = createMutation.isPending || updateMutation.isPending || loadPortfolioDetailQuery.isLoading;



    return (
        <FormDialog
            open={control.isVisible}
            onOpenChange={(open) => {
                if (!open) {
                    form.reset({
                        title: "",
                        description: "",
                        skill_used: undefined,
                        is_featured: false,
                    });
                    control.hide();
                }
            }}
            title={isEditMode ? "Edit Portfolio Item" : "Create Portfolio Item"}
            description={isEditMode ? "Update the portfolio item details" : "Add a new portfolio item"}
            onSubmit={form.handleSubmit(onSubmit)}
            onCancel={handleCancel}
            isLoading={isLoading}
            submitText={isEditMode ? "Update" : "Create"}
            maxWidth="4xl"
        >
            <Form {...form}>
                <div className="space-y-4">
                    <FormField
                        control={form.control}
                        name="title"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Title *</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="Enter project title"
                                        {...field}
                                        disabled={isLoading}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="skill_used"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Skill Used *</FormLabel>
                                <FormControl>
                                    <ComboBox2
                                        title="Search and select a skill..."
                                        value={field.value}
                                        valueKey="id"
                                        multiple={false}
                                        disabled={isLoading}
                                        renderLabel={(skill) => skill.name}
                                        searchFn={searchSkills}
                                        onChange={field.onChange}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="description"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Description</FormLabel>
                                <FormControl>
                                    <Textarea
                                        placeholder="Enter project description..."
                                        className="min-h-[120px]"
                                        {...field}
                                        disabled={isLoading}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="is_featured"
                        render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                                <FormControl>
                                    <Checkbox
                                        checked={field.value}
                                        onCheckedChange={field.onChange}
                                        disabled={isLoading}
                                    />
                                </FormControl>
                                <div className="space-y-1 leading-none">
                                    <FormLabel>Featured Project</FormLabel>
                                    <p className="text-sm text-muted-foreground">
                                        Mark this project as featured to highlight it in your portfolio
                                    </p>
                                </div>
                            </FormItem>
                        )}
                    />

                    {isEditMode && (
                        <AttachmentsView
                            attachments={loadPortfolioAttachmentsQuery.data || []}
                            onUpload={async (files) => {
                                const formData = new FormData();
                                files.forEach((file) => {
                                    formData.append('files', file);
                                });

                                await myApi.axios.post(
                                    `/api/v1/users/my/portfolio/${control.data!.id}/attachments/`,
                                    formData,
                                    {
                                        headers: {
                                            'Content-Type': 'multipart/form-data',
                                        },
                                    }
                                );

                                return { success: true, files };
                            }}
                            onDelete={async (attachment) => {
                                await myApi.v1UsersMyPortfolioAttachmentsDestroy({
                                    id: attachment.id.toString(),
                                    portfolioId: control.data!.id!.toString()
                                });
                            }}
                            onUploadSuccess={() => {
                                queryClient.invalidateQueries({ queryKey: loadPortfolioAttachmentsQueryKey });
                                queryClient.invalidateQueries({ queryKey: ['portfolio'] });
                            }}
                            onDeleteSuccess={() => {
                                queryClient.invalidateQueries({ queryKey: loadPortfolioAttachmentsQueryKey });
                                queryClient.invalidateQueries({ queryKey: ['portfolio'] });
                            }}
                            isLoading={isLoading}
                            title="Attachments"
                            description="Upload files to attach to this portfolio item"
                        />
                    )}

                </div>
            </Form>
        </FormDialog>
    );
}
