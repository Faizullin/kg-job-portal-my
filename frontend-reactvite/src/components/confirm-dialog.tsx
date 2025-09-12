import { cn } from "@/lib/utils";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { useDialogControl } from "@/hooks/use-dialog-control";

type ConfirmDialogProps = {
  control: ReturnType<typeof useDialogControl<any>>;
  title: React.ReactNode;
  disabled?: boolean;
  desc: React.JSX.Element | string;
  cancelBtnText?: string;
  confirmText?: React.ReactNode;
  destructive?: boolean;
  onConfirm: () => void;
  onCancel?: () => void;
  isLoading?: boolean;
  className?: string;
  children?: React.ReactNode;
};

export function ConfirmDialog(props: ConfirmDialogProps) {
  const {
    control,
    title,
    desc,
    children,
    className,
    confirmText,
    cancelBtnText,
    destructive,
    isLoading,
    disabled = false,
    onConfirm,
    onCancel,
  } = props;

  const { isVisible, hide } = control;

  const handleCancel = () => {
    hide();
    onCancel?.();
  };

  const handleConfirm = () => {
    onConfirm();
    hide();
  };

  return (
    <AlertDialog open={isVisible} onOpenChange={handleCancel}>
      <AlertDialogContent className={cn(className && className)}>
        <AlertDialogHeader className="text-start">
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription asChild>
            <div>{desc}</div>
          </AlertDialogDescription>
        </AlertDialogHeader>
        {children}
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading} onClick={handleCancel}>
            {cancelBtnText ?? "Cancel"}
          </AlertDialogCancel>
          <Button
            variant={destructive ? "destructive" : "default"}
            onClick={handleConfirm}
            disabled={disabled || isLoading}
          >
            {confirmText ?? "Continue"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
