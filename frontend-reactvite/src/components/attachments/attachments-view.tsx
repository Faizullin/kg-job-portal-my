import { AttachmentUploadNiceDialog } from "@/components/dialogs/attachment-upload-nice-dialog";
import { DeleteConfirmNiceDialog } from "@/components/dialogs/delete-confirm-dialog";
import NiceModal from "@/components/nice-modal/modal-context";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Attachment } from "@/lib/api/axios-client";
import { File, FileText, Grid3X3, Image as ImageIcon, List, Paperclip, X } from "lucide-react";
import { useCallback, useState } from "react";
import { toast } from "sonner";

interface AttachmentsViewProps {
    attachments: Attachment[];
    onUpload: (files: File[]) => Promise<{ success: boolean; files: File[]; error?: string }>;
    onDelete: (attachment: Attachment) => Promise<void>;
    onUploadSuccess?: () => void;
    onDeleteSuccess?: () => void;
    isLoading?: boolean;
    className?: string;
    title?: string;
    description?: string;
}

export function AttachmentsView({
    attachments,
    onUpload,
    onDelete,
    onUploadSuccess,
    onDeleteSuccess,
    isLoading = false,
    className = "",
    title = "Attachments",
    description = "Upload files to attach",
}: AttachmentsViewProps) {
    const [attachmentViewMode, setAttachmentViewMode] = useState<'grid' | 'list'>('grid');

    const handleDeleteAttachment = useCallback(async (attachment: Attachment) => {
        try {
            await NiceModal.show(DeleteConfirmNiceDialog, {
                args: {
                    title: "Delete Attachment",
                    desc: `Are you sure you want to delete "${attachment.original_filename}"? This action cannot be undone.`,
                    confirmText: "Delete",
                }
            });

            await onDelete(attachment);
            onDeleteSuccess?.();
            toast.success("Attachment deleted successfully!");
        } catch (error: any) {
            if (error.reason === "cancel") return;
            toast.error("Failed to delete attachment");
        }
    }, [onDelete, onDeleteSuccess]);

    const handleUploadAttachments = useCallback(async () => {
        try {
            const result = await NiceModal.show(AttachmentUploadNiceDialog, {
                args: {
                    title: "Upload Attachments",
                    description,
                    maxFiles: 5,
                    acceptedFileTypes: {
                        'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
                        'application/pdf': ['.pdf'],
                        'text/*': ['.txt', '.md'],
                        'application/msword': ['.doc'],
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
                    },
                    maxFileSize: 10 * 1024 * 1024, // 10MB
                    uploadFn: onUpload,
                }
            });

            if (result?.files?.length > 0) {
                onUploadSuccess?.();
                toast.success("Files uploaded successfully!");
            }
        } catch (error: any) {
            if (error.reason === "cancel") return;
            toast.error("Failed to upload files");
        }
    }, [onUpload, onUploadSuccess, description]);

    const getFileIcon = useCallback((mimeType?: string) => {
        if (mimeType?.startsWith('image/')) {
            return <ImageIcon className="h-4 w-4 text-blue-500" />;
        }
        if (mimeType?.includes('pdf')) {
            return <File className="h-4 w-4 text-red-500" />;
        }
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }, []);

    const isImageFile = useCallback((mimeType?: string) => {
        return mimeType?.startsWith('image/') || false;
    }, []);

    return (
        <div className={`space-y-3 pt-4 border-t ${className}`}>
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">{title}</h3>
                <div className="flex items-center gap-2">
                    <div className="flex items-center border rounded-md">
                        <Button
                            type="button"
                            variant={attachmentViewMode === 'grid' ? 'default' : 'ghost'}
                            size="sm"
                            onClick={() => setAttachmentViewMode('grid')}
                            className="h-8 px-2"
                        >
                            <Grid3X3 className="h-4 w-4" />
                        </Button>
                        <Button
                            type="button"
                            variant={attachmentViewMode === 'list' ? 'default' : 'ghost'}
                            size="sm"
                            onClick={() => setAttachmentViewMode('list')}
                            className="h-8 px-2"
                        >
                            <List className="h-4 w-4" />
                        </Button>
                    </div>
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleUploadAttachments}
                        disabled={isLoading}
                        className="flex items-center gap-2"
                    >
                        <Paperclip className="h-4 w-4" />
                        Upload Files
                    </Button>
                </div>
            </div>

            <div className="min-h-[120px] border rounded-lg p-4 bg-muted/30">
                {attachments && attachments.length > 0 ? (
                    attachmentViewMode === 'grid' ? (
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                            {attachments.map((attachment, index) => (
                                <div key={index} className="relative group bg-background rounded-lg border p-3 hover:shadow-sm transition-shadow">
                                    <div className="flex flex-col items-center space-y-2">
                                        {isImageFile(attachment.mime_type) ? (
                                            <div className="w-12 h-12 bg-muted rounded flex items-center justify-center overflow-hidden">
                                                <img
                                                    src={attachment.file_url}
                                                    alt={attachment.original_filename}
                                                    className="w-full h-full object-cover"
                                                    onError={(e) => {
                                                        e.currentTarget.style.display = 'none';
                                                        const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                                                        if (nextElement) {
                                                            nextElement.style.display = 'flex';
                                                        }
                                                    }}
                                                />
                                                <div className="w-full h-full flex items-center justify-center" style={{ display: 'none' }}>
                                                    {getFileIcon(attachment.mime_type)}
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="w-12 h-12 bg-muted rounded flex items-center justify-center">
                                                {getFileIcon(attachment.mime_type)}
                                            </div>
                                        )}
                                        <div className="text-center w-full">
                                            <p className="text-xs font-medium truncate w-full px-1" title={attachment.original_filename}>
                                                {attachment.original_filename || `Attachment ${index + 1}`}
                                            </p>
                                            <p className="text-xs text-muted-foreground truncate w-full px-1">
                                                {attachment.size ? `${(attachment.size / 1024).toFixed(1)} KB` : 'Unknown size'}
                                            </p>
                                        </div>
                                    </div>
                                    <Button
                                        type="button"
                                        variant="ghost"
                                        size="sm"
                                        className="absolute top-1 right-1 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive bg-background/80 backdrop-blur-sm"
                                        onClick={() => handleDeleteAttachment(attachment)}
                                    >
                                        <X className="h-3 w-3" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {attachments.map((attachment, index) => (
                                <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                                    <div className="flex items-center gap-2 min-w-0 flex-1">
                                        {isImageFile(attachment.mime_type) ? (
                                            <div className="w-8 h-8 bg-muted rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                                                <img
                                                    src={attachment.file_url}
                                                    alt={attachment.original_filename}
                                                    className="w-full h-full object-cover"
                                                    onError={(e) => {
                                                        e.currentTarget.style.display = 'none';
                                                        const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                                                        if (nextElement) {
                                                            nextElement.style.display = 'flex';
                                                        }
                                                    }}
                                                />
                                                <div className="w-full h-full flex items-center justify-center" style={{ display: 'none' }}>
                                                    <ImageIcon className="h-4 w-4 text-blue-500" />
                                                </div>
                                            </div>
                                        ) : (
                                            <FileText className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                        )}
                                        <div className="min-w-0 flex-1">
                                            <span className="text-sm font-medium truncate block" title={attachment.original_filename}>
                                                {attachment.original_filename || `Attachment ${index + 1}`}
                                            </span>
                                        </div>
                                        <Badge variant="secondary" className="text-xs flex-shrink-0">
                                            {attachment.size ? `${(attachment.size / 1024).toFixed(1)} KB` : 'Unknown size'}
                                        </Badge>
                                    </div>
                                    <Button
                                        type="button"
                                        variant="ghost"
                                        size="sm"
                                        className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive flex-shrink-0"
                                        onClick={() => handleDeleteAttachment(attachment)}
                                    >
                                        <X className="h-3 w-3" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    )
                ) : (
                    <div className="flex flex-col items-center justify-center h-20 text-muted-foreground">
                        <Paperclip className="h-8 w-8 mb-2" />
                        <p className="text-sm">No attachments yet</p>
                        <p className="text-xs">Click "Upload Files" to add attachments</p>
                    </div>
                )}
            </div>
        </div>
    );
}
