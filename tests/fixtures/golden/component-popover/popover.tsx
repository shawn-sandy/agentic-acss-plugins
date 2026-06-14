export interface PopoverProps {
  /** Unique ID — defaults to a generated id; required for popovertarget linking */
  id?: string
  /** Content rendered inside the popover */
  children: React.ReactNode
  /** Custom trigger element (default: `<button>` with triggerLabel) */
  trigger?: React.ReactNode
  /** aria-label for the default trigger button */
  triggerLabel?: string
  /** "auto" (light dismiss) or "manual" (explicit close required) */
  mode?: 'auto' | 'manual'
  /** Visual placement hint relative to the trigger */
  placement?: 'top' | 'bottom' | 'left' | 'right'
  /** Controlled open state */
  isOpen?: boolean
  /** Toggle callback */
  onToggle?: (open: boolean) => void
  /** Show close button (default: true for manual mode, false for auto) */
  showCloseButton?: boolean
  /** aria-label for the close button */
  closeButtonLabel?: string
  /** Show positioning arrow (default: true) */
  showArrow?: boolean
  /** Custom CSS class on the popover element */
  className?: string
  /** Inline CSS variables / styles */
  styles?: React.CSSProperties
}

import React, { useEffect, useId, useRef } from 'react'

export interface PopoverProps {
  id?: string
  children: React.ReactNode
  trigger?: React.ReactNode
  triggerLabel?: string
  mode?: 'auto' | 'manual'
  placement?: 'top' | 'bottom' | 'left' | 'right'
  isOpen?: boolean
  onToggle?: (open: boolean) => void
  showCloseButton?: boolean
  closeButtonLabel?: string
  showArrow?: boolean
  className?: string
  styles?: React.CSSProperties
}

export const Popover: React.FC<PopoverProps> = ({
  id,
  children,
  trigger,
  triggerLabel = 'Open',
  mode = 'auto',
  placement = 'bottom',
  isOpen,
  onToggle,
  showCloseButton,
  showArrow = true,
  closeButtonLabel = 'Close',
  className = '',
  styles,
}) => {
  const generatedId = useId()
  const popoverId = id || generatedId
  const popoverRef = useRef<HTMLDivElement>(null)

  const shouldShowCloseButton =
    showCloseButton !== undefined ? showCloseButton : mode === 'manual'

  // Controlled open state — drive showPopover() / hidePopover()
  useEffect(() => {
    const popover = popoverRef.current
    if (!popover || isOpen === undefined) return

    try {
      const isCurrentlyOpen =
        popover.matches(':popover-open') || popover.hasAttribute('data-popover-open')
      if (isOpen && !isCurrentlyOpen) popover.showPopover()
      else if (!isOpen && isCurrentlyOpen) popover.hidePopover()
    } catch {
      const isCurrentlyOpen = popover.hasAttribute('data-popover-open')
      if (isOpen && !isCurrentlyOpen) popover.showPopover()
      else if (!isOpen && isCurrentlyOpen) popover.hidePopover()
    }
  }, [isOpen])

  // Toggle callback — listen to the native ToggleEvent
  useEffect(() => {
    const popover = popoverRef.current
    if (!popover || !onToggle) return

    const handleToggle = (event: Event) => {
      const toggleEvent = event as ToggleEvent
      onToggle(toggleEvent.newState === 'open')
    }
    popover.addEventListener('toggle', handleToggle)
    return () => popover.removeEventListener('toggle', handleToggle)
  }, [onToggle])

  const renderTrigger = () => {
    if (trigger) {
      return React.cloneElement(trigger as React.ReactElement, {
        popovertarget: popoverId,
        popovertargetaction: 'toggle',
      })
    }
    return (
      <button
        type="button"
        popovertarget={popoverId}
        popovertargetaction="toggle"
        aria-label={triggerLabel}
        className="popover-trigger"
      >
        {triggerLabel}
      </button>
    )
  }

  return (
    <>
      {renderTrigger()}
      <div
        ref={popoverRef}
        id={popoverId}
        popover={mode}
        className={`popover ${className}`.trim()}
        data-placement={placement}
        style={styles}
      >
        {showArrow && <div className="popover-arrow" data-placement={placement} />}
        <div className="popover-content">
          {children}
          {shouldShowCloseButton && (
            <button
              type="button"
              popovertarget={popoverId}
              popovertargetaction="hide"
              aria-label={closeButtonLabel}
              className="popover-close"
            >
              ×
            </button>
          )}
        </div>
      </div>
    </>
  )
}

Popover.displayName = 'Popover'
export default Popover