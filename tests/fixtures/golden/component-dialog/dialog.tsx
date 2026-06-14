export type DialogProps = {
  /** Ref to the dialog element — required for showModal()/close() */
  dialogRef: React.RefObject<HTMLDialogElement>
  /** Whether to open on mount */
  openOnMount?: boolean
  /** Callback when dialog is closed */
  onClose?: () => void
  /** Dialog title for aria-labelledby */
  title?: string
  /** Dialog description for aria-describedby */
  description?: string
  /** Whether to show a close button in the header */
  showCloseButton?: boolean
  /** Dialog content */
  children?: React.ReactNode
  /** Footer action buttons */
  footer?: React.ReactNode
  /** CSS class name */
  classes?: string
  /** Inline styles */
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'dialog'>, 'open'>

export type DialogHeaderProps = {
  children?: React.ReactNode
  onClose?: () => void
  showCloseButton?: boolean
  classes?: string
}

export type DialogBodyProps = {
  children?: React.ReactNode
  classes?: string
}

export type DialogFooterProps = {
  children?: React.ReactNode
  classes?: string
}

import UI from '../ui'
import React from 'react'
import Button from '../button/button'

// --- Types (inline) ---
// [DialogProps, DialogHeaderProps, DialogBodyProps, DialogFooterProps as above]

// --- Sub-components ---
const DialogHeader = ({ children, onClose, showCloseButton = true, classes }: DialogHeaderProps) => (
  <UI as="div" classes={`dialog-header${classes ? ' ' + classes : ''}`}>
    <UI as="div" classes="dialog-header-content">{children}</UI>
    {showCloseButton && (
      <Button
        type="button"
        variant="icon"
        aria-label="Close dialog"
        onClick={onClose}
        classes="dialog-close"
      >
        ×
      </Button>
    )}
  </UI>
)
DialogHeader.displayName = 'Dialog.Header'

const DialogBody = ({ children, classes }: DialogBodyProps) => (
  <UI as="div" classes={`dialog-body${classes ? ' ' + classes : ''}`}>
    {children}
  </UI>
)
DialogBody.displayName = 'Dialog.Body'

const DialogFooter = ({ children, classes }: DialogFooterProps) => (
  <UI as="div" classes={`dialog-footer${classes ? ' ' + classes : ''}`}>
    {children}
  </UI>
)
DialogFooter.displayName = 'Dialog.Footer'

// --- Root component ---
const DialogRoot = React.forwardRef<HTMLDialogElement, DialogProps>(({
  dialogRef,
  openOnMount,
  onClose,
  title,
  description,
  showCloseButton = true,
  children,
  footer,
  classes,
  styles,
  ...props
}: DialogProps, _ref) => {
  const titleId = title ? `dialog-title-${Math.random().toString(36).slice(2, 7)}` : undefined

  const handleClose = () => {
    dialogRef.current?.close()
    onClose?.()
  }

  const handleBackdropClick = (e: React.MouseEvent<HTMLDialogElement>) => {
    if (e.currentTarget === e.target) handleClose()
  }

  return (
    <UI
      as="dialog"
      ref={dialogRef}
      open={openOnMount}
      classes={`dialog${classes ? ' ' + classes : ''}`}
      styles={styles}
      aria-labelledby={titleId}
      onClick={handleBackdropClick}
      {...props}
    >
      {title && (
        <DialogHeader onClose={handleClose} showCloseButton={showCloseButton}>
          <UI as="h2" id={titleId} classes="dialog-title">{title}</UI>
          {description && <UI as="p" classes="dialog-description">{description}</UI>}
        </DialogHeader>
      )}
      <DialogBody>{children}</DialogBody>
      {footer && <DialogFooter>{footer}</DialogFooter>}
    </UI>
  )
})
DialogRoot.displayName = 'Dialog'

// --- Compound assembly ---
type DialogComponent = typeof DialogRoot & {
  Header: typeof DialogHeader
  Body: typeof DialogBody
  Footer: typeof DialogFooter
}

export const Dialog = Object.assign(DialogRoot, {
  Header: DialogHeader,
  Body: DialogBody,
  Footer: DialogFooter,
}) as DialogComponent

export default Dialog