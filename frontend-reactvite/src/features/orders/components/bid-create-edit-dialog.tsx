import { FormDialog } from "@/components/dialogs/form-dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useDialogControl } from "@/hooks/use-dialog-control";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

const bidFormSchema = z.object({
  id: z.number().optional(),
  order_id: z.number(),
  amount: z.number().min(0.01, "Amount must be greater than 0"),
  description: z.string().min(1, "Description is required"),
  estimated_duration: z.number().min(1, "Duration must be at least 1 hour"),
  terms_conditions: z.string().optional(),
  is_negotiable: z.boolean(),
});

export type BidFormData = z.infer<typeof bidFormSchema>;

interface BidCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<BidFormData>>;
  onSave: (data: BidFormData) => void;
  onCancel?: () => void;
}

export function BidCreateEditDialog({
  control,
  onSave,
  onCancel
}: BidCreateEditDialogProps) {
  const { isVisible, data, hide } = control;
  const isEdit = !!data?.id;

  const form = useForm<BidFormData>({
    resolver: zodResolver(bidFormSchema),
    defaultValues: data || {
      order_id: 0,
      amount: 0,
      description: "",
      estimated_duration: 0,
      terms_conditions: "",
      is_negotiable: false,
    }
  });

  const handleClose = () => {
    form.reset();
    hide();
    onCancel?.();
  };

  const onSubmit = (formData: BidFormData) => {
    onSave(formData);
    handleClose();
  };

  return (
    <FormDialog
      open={isVisible}
      onOpenChange={handleClose}
      title={isEdit ? 'Edit Bid' : 'Create New Bid'}
      description={isEdit
        ? 'Update your bid details below.'
        : 'Submit your bid for this order.'
      }
      onSubmit={form.handleSubmit(onSubmit)}
      onCancel={handleClose}
      submitText={isEdit ? 'Update Bid' : 'Submit Bid'}
      maxWidth="lg"
    >
      <Form {...form}>
        <form className="space-y-6">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="amount"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Bid Amount ($) *</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="150.00"
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value))}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="estimated_duration"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Estimated Duration (hours) *</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="4"
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value))}
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
                  <FormLabel>Bid Description *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe your approach and what you'll deliver..."
                      rows={4}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="terms_conditions"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Terms & Conditions</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Any specific terms or conditions for this bid..."
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="is_negotiable"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>Price is negotiable</FormLabel>
                  </div>
                </FormItem>
              )}
            />
          </div>
        </form>
      </Form>
    </FormDialog>
  );
}