import { useCallback } from "react";
import { ConfirmDialog } from "../confirm-dialog";
import NiceModal, { type NiceModalHocPropsExtended } from "../nice-modal/modal-context";

export const DeleteConfirmNiceDialog = NiceModal.create<NiceModalHocPropsExtended<{
    args: {
        title: string;
        desc: string;
        confirmText?: string;
    };
}>, {
    reason: "confirm" | "cancel";
}>
    (({ args }) => {
        const modal = NiceModal.useModal();
        const handleConfirm = useCallback(() => {
            modal.resolve({
                reason: "confirm",
            });
        }, [modal]);
        const handleCancel = useCallback(() => {
            modal.resolve({
                reason: "cancel",
            });
        }, [modal]);
        return (
            <ConfirmDialog
                control={{
                    isVisible: modal.visible,
                    hide: modal.hide,
                    show: modal.show,
                    toggle: () => modal.visible ? modal.hide() : modal.show(),
                    data: undefined,
                }}
                onConfirm={handleConfirm}
                onCancel={handleCancel}
                title={args.title}
                desc={args.desc}
                confirmText={args.confirmText || "Delete"}
            />
        );
    });

