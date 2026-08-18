"use client";

import { useEffect, useRef } from "react";

type ClearConversationProps = {
  open: boolean;
  onRequest: () => void;
  onConfirm: () => void;
  onClose: () => void;
};

export function ClearConversation({ open, onRequest, onConfirm, onClose }: ClearConversationProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const node = dialogRef.current;
    if (!node || typeof node.showModal !== "function") {
      return;
    }
    if (open && !node.open) {
      node.showModal();
    }
    if (!open && node.open) {
      node.close();
    }
  }, [open]);

  return (
    <>
      <button
        type="button"
        className="control control--quiet"
        onClick={onRequest}
        aria-label="Clear conversation"
      >
        Clear conversation
      </button>
      <dialog
        ref={dialogRef}
        className="dialog"
        aria-labelledby="clear-title"
        onClose={onClose}
        onCancel={onClose}
      >
        <h2 id="clear-title">Clear this conversation?</h2>
        <p>This removes the visible transcript and Pixel short-term conversation context.</p>
        <div className="controls">
          <button type="button" className="control control--primary" onClick={onConfirm}>
            Clear conversation
          </button>
          <button type="button" className="control" onClick={onClose}>
            Keep conversation
          </button>
        </div>
      </dialog>
    </>
  );
}
