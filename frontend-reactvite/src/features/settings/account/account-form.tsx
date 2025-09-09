import React from "react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { CaretSortIcon, CheckIcon } from "@radix-ui/react-icons";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { showSubmittedData } from "@/lib/show-submitted-data";
import { cn } from "@/lib/utils";
import { AuthClient } from "@/lib/auth/auth-client";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { DatePicker } from "@/components/date-picker";

const languages = [
  { label: "English", value: "en" },
  { label: "French", value: "fr" },
  { label: "German", value: "de" },
  { label: "Spanish", value: "es" },
  { label: "Portuguese", value: "pt" },
  { label: "Russian", value: "ru" },
  { label: "Japanese", value: "ja" },
  { label: "Korean", value: "ko" },
  { label: "Chinese", value: "zh" },
] as const;

const accountFormSchema = z.object({
  name: z
    .string()
    .min(1, "Please enter your name.")
    .min(2, "Name must be at least 2 characters.")
    .max(30, "Name must not be longer than 30 characters."),
  dob: z.date("Please select your date of birth."),
  language: z.string("Please select a language."),
});

type AccountFormValues = z.infer<typeof accountFormSchema>;

// Query key for user account data
const ACCOUNT_QUERY_KEY = ["user-account"];

// Fetch user account data
const fetchUserAccount = async (): Promise<AccountFormValues> => {
  const backendUser = AuthClient.getCurrentUser();
  const firebaseUser = AuthClient.getCurrentFirebaseUser();
  
  if (!backendUser || !firebaseUser) {
    throw new Error("User not authenticated");
  }

  return {
    name: backendUser.username || firebaseUser.displayName || "",
    dob: new Date(), // Add date of birth to backend user if needed
    language: "en", // Add language preference to backend user if needed
  };
};

// Update user account mutation
const updateUserAccount = async (data: AccountFormValues): Promise<void> => {
  // Simulate API call - replace with actual API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  console.log("Account update data:", data);
  // Here you would make the actual API call to update the account
};

export function AccountForm() {
  const queryClient = useQueryClient();

  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountFormSchema),
    defaultValues: {
      name: "",
      dob: new Date(),
      language: "",
    },
  });

  // Fetch user account data
  const { data: accountData, isLoading, error } = useQuery({
    queryKey: ACCOUNT_QUERY_KEY,
    queryFn: fetchUserAccount,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  // Update account mutation
  const updateAccountMutation = useMutation({
    mutationFn: updateUserAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ACCOUNT_QUERY_KEY });
      toast.success("Account updated successfully!");
    },
    onError: (error) => {
      console.error("Error updating account:", error);
      toast.error("Failed to update account");
    },
  });

  // Update form when data is loaded
  React.useEffect(() => {
    if (accountData) {
      form.reset(accountData);
    }
  }, [accountData, form]);

  const onSubmit = (data: AccountFormValues) => {
    showSubmittedData(data);
    updateAccountMutation.mutate(data);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-sm text-muted-foreground">Loading account...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-sm text-destructive">Failed to load account data</div>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="Your name" {...field} />
              </FormControl>
              <FormDescription>
                This is the name that will be displayed on your profile and in
                emails.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="dob"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>Date of birth</FormLabel>
              <DatePicker selected={field.value} onSelect={field.onChange} />
              <FormDescription>
                Your date of birth is used to calculate your age.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="language"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>Language</FormLabel>
              <Popover>
                <PopoverTrigger asChild>
                  <FormControl>
                    <Button
                      variant="outline"
                      role="combobox"
                      className={cn(
                        "w-[200px] justify-between",
                        !field.value && "text-muted-foreground",
                      )}
                    >
                      {field.value
                        ? languages.find(
                            (language) => language.value === field.value,
                          )?.label
                        : "Select language"}
                      <CaretSortIcon className="ms-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent className="w-[200px] p-0">
                  <Command>
                    <CommandInput placeholder="Search language..." />
                    <CommandEmpty>No language found.</CommandEmpty>
                    <CommandGroup>
                      <CommandList>
                        {languages.map((language) => (
                          <CommandItem
                            value={language.label}
                            key={language.value}
                            onSelect={() => {
                              form.setValue("language", language.value);
                            }}
                          >
                            <CheckIcon
                              className={cn(
                                "size-4",
                                language.value === field.value
                                  ? "opacity-100"
                                  : "opacity-0",
                              )}
                            />
                            {language.label}
                          </CommandItem>
                        ))}
                      </CommandList>
                    </CommandGroup>
                  </Command>
                </PopoverContent>
              </Popover>
              <FormDescription>
                This is the language that will be used in the dashboard.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={updateAccountMutation.isPending}>
          {updateAccountMutation.isPending ? "Updating..." : "Update account"}
        </Button>
      </form>
    </Form>
  );
}
