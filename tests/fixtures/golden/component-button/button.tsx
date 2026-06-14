/**
 * Props for the Button component.
 *
 * Uses `aria-disabled` instead of the native `disabled` attribute so the
 * element stays in the tab order and remains reachable by keyboard users
 * (WCAG 2.1.1 — Keyboard). Style, size, and color variants are applied via
 * HTML data attributes; see the SCSS template for the corresponding selectors.
 *
 * @see Button
 */
export type ButtonProps = {
  /** Required — prevents implicit submit in forms */
  type: 'button' | 'submit' | 'reset'

  /** Button content */
  children?: React.ReactNode

  /** Accessible disabled — keeps element in tab order (WCAG 2.1.1) */
  disabled?: boolean

  /** Legacy compat. `disabled` takes precedence. */
  isDisabled?: boolean

  /** Maps to data-btn attribute: xs | sm | md | lg | xl | 2xl */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'

  /** Maps to data-style attribute: outline | pill | text | icon */
  variant?: 'text' | 'pill' | 'icon' | 'outline'

  /** Maps to data-color attribute: primary | secondary | danger | success | warning */
  color?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning'

  /** Stretches button to 100% width (adds 'block' to data-btn) */
  block?: boolean

  /** CSS class name via classes prop (takes precedence over className) */
  classes?: string

  /** Inline styles (passed to UI) */
  styles?: React.CSSProperties

  /** Raw data-btn tokens merged with size/block */
  'data-btn'?: string

  onClick?: React.MouseEventHandler<HTMLButtonElement>
  onKeyDown?: React.KeyboardEventHandler<HTMLButtonElement>
  onPointerDown?: React.PointerEventHandler<HTMLButtonElement>
  onPointerOver?: React.PointerEventHandler<HTMLButtonElement>
  onPointerLeave?: React.PointerEventHandler<HTMLButtonElement>
} & Omit<React.ComponentPropsWithoutRef<'button'>, 'disabled'>

import UI from '../ui'
import React from 'react'

/**
 * Resolves the active disabled state from `disabled` and legacy `isDisabled`
 * props. `disabled` takes precedence; both default to `false` if absent.
 *
 * @internal - inlined into button.tsx; do not extract to a shared module.
 */
// One-liner helper — inline in button.tsx
const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false

/**
 * Manages accessible disabled state for interactive elements.
 *
 * Blocks click/keydown/pointerdown handlers when `disabled` is true while
 * keeping the element focusable and announcing its state via `aria-disabled`.
 * Do not use native `disabled` on elements where keyboard reach matters.
 *
 * @internal - inlined into button.tsx; do not extract to a shared module.
 */
// Inline in button.tsx — do not create a separate file
function useDisabledState<T extends HTMLElement = HTMLButtonElement>(
  disabled: boolean | undefined,
  handlers: {
    onClick?: (e: React.MouseEvent<T>) => void
    onKeyDown?: (e: React.KeyboardEvent<T>) => void
    onPointerDown?: (e: React.PointerEvent<T>) => void
  } = {},
  className?: string
) {
  const isDisabled = Boolean(disabled)
  const mergedClassName = [isDisabled ? 'is-disabled' : '', className]
    .filter(Boolean).join(' ')

  const wrap = <E,>(fn?: (e: E) => void) => fn
    ? (e: any) => { if (isDisabled) { e.preventDefault(); e.stopPropagation(); return } fn(e) }
    : undefined

  return {
    disabledProps: { 'aria-disabled': isDisabled, className: mergedClassName },
    handlers: {
      onClick: wrap(handlers.onClick),
      onKeyDown: wrap(handlers.onKeyDown),
      onPointerDown: wrap(handlers.onPointerDown),
    },
  }
}


/**
 * Accessible button with size, style, and color variants.
 *
 * Replaces the native `disabled` attribute with `aria-disabled` so the button
 * stays keyboard-reachable even when functionally inactive (WCAG 2.1.1).
 * Variants are driven by data attributes (`data-btn`, `data-style`,
 * `data-color`) and styled entirely via CSS custom properties — no inline
 * styles required for theming.
 *
 * @param props - {@link ButtonProps}
 *
 * @example
 * // Primary submit button
 * <Button type="submit" color="primary">Save changes</Button>
 *
 * @example
 * // Large outline button, accessible disabled
 * <Button type="button" variant="outline" size="lg" disabled>
 *   Unavailable
 * </Button>
 */
export const Button = ({
  type = 'button',
  children,
  styles,
  disabled,
  isDisabled,
  classes,
  size,
  variant,
  color,
  block,
  onPointerDown,
  onPointerOver,
  onPointerLeave,
  onClick,
  onKeyDown,
  ...props
}: ButtonProps) => {
  const isActuallyDisabled = resolveDisabledState(disabled, isDisabled)
  const { disabledProps, handlers } = useDisabledState(
    isActuallyDisabled,
    { onClick, onPointerDown, onKeyDown },
    classes,
  )

  const { 'data-btn': dataBtnProp, ...restProps } = props
  const dataBtnValue = [size, block ? 'block' : undefined, dataBtnProp]
    .filter(Boolean).join(' ') || undefined

  return (
    <UI
      as="button"
      type={type}
      data-btn={dataBtnValue}
      data-style={variant}
      data-color={color}
      aria-disabled={disabledProps['aria-disabled']}
      onPointerOver={onPointerOver}
      onPointerLeave={onPointerLeave}
      style={styles}
      className={disabledProps.className}
      {...restProps}
      {...handlers}
    >
      {children}
    </UI>
  )
}

export default Button
Button.displayName = 'Button'