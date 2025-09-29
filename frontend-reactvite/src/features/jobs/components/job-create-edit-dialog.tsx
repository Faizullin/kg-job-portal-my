import { FormDialog } from "@/components/dialogs/form-dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useDialogControl } from "@/hooks/use-dialog-control";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const jobFormSchema = z.object({
  id: z.number().optional(),
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  service_category: z.string().min(1, "Service category is required"),
  service_subcategory: z.string().optional(),
  location: z.string().min(1, "Location is required"),
  city: z.string().min(1, "City is required"),
  state: z.string().min(1, "State is required"),
  country: z.string().min(1, "Country is required"),
  postal_code: z.string().min(1, "Postal code is required"),
  service_date: z.string().min(1, "Service date is required"),
  service_time: z.string().min(1, "Service time is required"),
  urgency: z.string().min(1, "Urgency is required"),
  budget_min: z.number().min(0, "Minimum budget must be positive").optional(),
  budget_max: z.number().min(0, "Maximum budget must be positive").optional(),
  special_requirements: z.string().optional(),
}).refine(
  (data) => {
    if (data.budget_min && data.budget_max) {
      return data.budget_max >= data.budget_min;
    }
    return true;
  },
  {
    message: "Maximum budget must be greater than or equal to minimum budget",
    path: ["budget_max"],
  }
);

export type JobFormData = z.infer<typeof jobFormSchema>;

interface JobCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<JobFormData>>;
  onSave?: (data: JobFormData) => void;
  onCancel?: () => void;
}

export function JobCreateEditDialog({
  control,
  onSave,
  onCancel
}: JobCreateEditDialogProps) {
  const { isVisible, data, hide } = control;
  const isEdit = !!data?.id;
  const queryClient = useQueryClient();

  const form = useForm<JobFormData>({
    resolver: zodResolver(jobFormSchema),
    defaultValues: data || {
      title: "",
      description: "",
      service_category: "",
      service_subcategory: "",
      location: "",
      city: "",
      service_date: "",
      service_time: "",
      urgency: "medium",
      budget_min: 0,
      budget_max: 0,
      special_requirements: "",
    }
  });

  const selectedCategory = form.watch("service_category");

  // Load service categories
  const categoriesQuery = useQuery({
    queryKey: ['service-categories'],
    queryFn: () => myApi.v1CoreServiceCategoriesList({ isActive: true, pageSize: 100 }).then(r => r.data),
    staleTime: 10 * 60 * 1000,
  });

  // Load service subcategories based on selected category
  const subcategoriesQuery = useQuery({
    queryKey: ['service-subcategories', selectedCategory],
    queryFn: async () => {
      if (!selectedCategory) return { results: [] };
      const categoryId = categoriesQuery.data?.results?.find(cat => cat.name === selectedCategory)?.id;
      if (!categoryId) return { results: [] };
      return myApi.v1CoreServiceSubcategoriesList({ category: categoryId, isActive: true, pageSize: 100 }).then(r => r.data);
    },
    enabled: !!selectedCategory,
    staleTime: 10 * 60 * 1000,
  });

  const citiesQuery = useQuery({
    queryKey: ['cities'],
    queryFn: async () => {
      const response = await myApi.v1LocationsCitiesList( );
      return response.data;
    },
    staleTime: 10 * 60 * 1000,
  });

  // Reset subcategory when category changes
  useEffect(() => {
    if (selectedCategory) {
      form.setValue("service_subcategory", "");
    }
  }, [selectedCategory, form]);

  const jobMutation = useMutation({
    mutationFn: async (formData: JobFormData) => {
      const categoryId = categoriesQuery.data?.results?.find(cat => cat.name === formData.service_category)?.id;
      if (!categoryId) {
        throw new Error("Please select a valid service category");
      }

      let subcategoryId: number | undefined;
      if (formData.service_subcategory) {
        subcategoryId = subcategoriesQuery.data?.results?.find(sub => sub.name === formData.service_subcategory)?.id;
      }

      const cityId = citiesQuery.data?.results?.find(city => city.name === formData.city)?.id;
      if (!cityId) {
        throw new Error("Please select a valid city");
      }

      const jobData = {
        title: formData.title,
        description: formData.description,
        service_category: categoryId,
        service_subcategory: subcategoryId || 0, // Default to 0 if no subcategory
        location: formData.location,
        city: cityId,
        service_date: formData.service_date,
        service_time: formData.service_time,
        urgency: formData.urgency as any, // Cast to any to handle enum type
        budget_min: (formData.budget_min || 0).toString(),
        budget_max: (formData.budget_max || 0).toString(),
        special_requirements: formData.special_requirements || "",
      };

      if (isEdit && data?.id) {
        const response = await myApi.v1JobsUpdate({ id: data.id, job: jobData });
        return response.data;
      } else {
        const response = await myApi.v1JobsCreate({ job: jobData });
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast.success(isEdit ? "Job updated successfully!" : "Job created successfully!");

      onSave?.(form.getValues());
      handleClose();
    },
    onError: (error) => {
      console.error("Job save error:", error);
      toast.error(error instanceof Error ? error.message : "Failed to save job");
    },
  });

  const handleClose = () => {
    form.reset();
    hide();
    onCancel?.();
  };

  const onSubmit = (formData: JobFormData) => {
    jobMutation.mutate(formData);
  };

  return (
    <FormDialog
      open={isVisible}
      onOpenChange={handleClose}
      title={isEdit ? 'Edit Job' : 'Create New Job'}
      description={isEdit
        ? 'Update the job details below.'
        : 'Fill out the form below to create a new service job.'
      }
      onSubmit={form.handleSubmit(onSubmit)}
      onCancel={handleClose}
      submitText={isEdit ? 'Update Job' : 'Create Job'}
      maxWidth="3xl"
      isLoading={jobMutation.isPending}
    >
      <Form {...form}>
        <form className="space-y-6">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Job Title *</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g., House Cleaning Service" {...field} />
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
                  <FormLabel>Description *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe the service you need in detail..."
                      rows={4}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="service_category"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Service Category *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder={categoriesQuery.isLoading ? "Loading..." : "Select category"} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {categoriesQuery.isLoading ? (
                          <SelectItem value="loading" disabled>Loading categories...</SelectItem>
                        ) : (
                          (categoriesQuery.data?.results || []).map((category) => (
                            <SelectItem key={category.id} value={category.name}>
                              {category.name}
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="urgency"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Urgency *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select urgency" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="urgent">Urgent</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Service Subcategory - only show if category is selected */}
            {selectedCategory && (
              <FormField
                control={form.control}
                name="service_subcategory"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Service Subcategory</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder={subcategoriesQuery.isLoading ? "Loading..." : "Select subcategory (optional)"} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {subcategoriesQuery.isLoading ? (
                          <SelectItem value="loading" disabled>Loading subcategories...</SelectItem>
                        ) : (subcategoriesQuery.data?.results || []).length > 0 ? (
                          (subcategoriesQuery.data?.results || []).map((subcategory) => (
                            <SelectItem key={subcategory.id} value={subcategory.name}>
                              {subcategory.name}
                            </SelectItem>
                          ))
                        ) : (
                          <SelectItem value="no-subcategories" disabled>No subcategories available</SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <FormField
              control={form.control}
              name="location"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Service Location *</FormLabel>
                  <FormControl>
                    <Input placeholder="Full address where service is needed" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>City *</FormLabel>
                    <FormControl>
                      <Input placeholder="City" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="state"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>State *</FormLabel>
                    <FormControl>
                      <Input placeholder="State" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="country"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Country *</FormLabel>
                    <FormControl>
                      <Input placeholder="Country" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="postal_code"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Postal Code *</FormLabel>
                    <FormControl>
                      <Input placeholder="12345" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="service_date"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Preferred Date *</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="service_time"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Preferred Time *</FormLabel>
                    <FormControl>
                      <Input type="time" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="budget_min"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Minimum Budget ($)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="100"
                        value={field.value || ""}
                        onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="budget_max"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Maximum Budget ($)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="200"
                        value={field.value || ""}
                        onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="special_requirements"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Special Requirements</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Any special requirements or notes..."
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </form>
      </Form>
    </FormDialog>
  );
}