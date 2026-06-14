type WithAriaLabel = { 'aria-label': string; 'aria-labelledby'?: never }
type WithAriaLabelledBy = { 'aria-labelledby': string; 'aria-label'?: never }

export type IconButtonProps = Omit<ButtonProps, 'children'> &
  (WithAriaLabel | WithAriaLabelledBy) & {
    /** The icon element rendered inside the button */
    icon: React.ReactNode
    /**
     * Optional text shown alongside the icon at desktop widths.
     * Visually hidden below the icon-label breakpoint via a media query
     * on `[data-icon-label]`, but always present in the accessibility
     * tree — screen readers announce it at every viewport size.
     */
    label?: string
    /** Required to prevent implicit submit in forms */
    type: 'button' | 'submit' | 'reset'
  }

import React from 'react'
import Button, { type ButtonProps } from '../button/button'

type WithAriaLabel = { 'aria-label': string; 'aria-labelledby'?: never }
type WithAriaLabelledBy = { 'aria-labelledby': string; 'aria-label'?: never }

export type IconButtonProps = Omit<ButtonProps, 'children'> &
  (WithAriaLabel | WithAriaLabelledBy) & {
    icon: React.ReactNode
    label?: string
    type: 'button' | 'submit' | 'reset'
  }

export const IconButton = ({
  icon,
  label,
  variant = 'icon',
  type = 'button',
  ...props
}: IconButtonProps) => (
  <Button
    variant={variant}
    data-icon-btn={label ? 'has-label' : 'icon'}
    {...props}
    type={type}
  >
    {icon}
    {label && <span data-icon-label>{label}</span>}
  </Button>
)

IconButton.displayName = 'IconButton'
export default IconButton