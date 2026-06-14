export type IconName =
  | 'info'
  | 'success'
  | 'warning'
  | 'error'
  | 'close'
  | 'chevron-down'
  | 'chevron-right'
  | 'check'
  | 'external-link'

export type IconProps = {
  /** Icon name from the built-in set */
  name: IconName
  /** SVG width/height in pixels (default: 16) */
  size?: number
  /** Stroke / fill color (default: currentColor) */
  color?: string
  /** Decorative icon — true means screen readers skip it (default: true) */
  'aria-hidden'?: boolean
  /** Required for non-decorative standalone icons */
  'aria-label'?: string
} & Omit<React.SVGProps<SVGSVGElement>, 'aria-hidden' | 'aria-label'>

import React from 'react'

export type IconName =
  | 'info'
  | 'success'
  | 'warning'
  | 'error'
  | 'close'
  | 'chevron-down'
  | 'chevron-right'
  | 'check'
  | 'external-link'


const ICON_PATHS: Record<IconName, React.ReactNode> = {
  info: (
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
  ),
  success: (
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
  ),
  warning: (
    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
  ),
  error: (
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
  ),
  close: (
    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
  ),
  'chevron-down': (
    <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" />
  ),
  'chevron-right': (
    <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z" />
  ),
  check: (
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
  ),
  'external-link': (
    <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z" />
  ),
}

export const Icon = ({
  name,
  size = 16,
  color = 'currentColor',
  'aria-hidden': ariaHidden = true,
  'aria-label': ariaLabel,
  ...props
}: IconProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={color}
    aria-hidden={ariaLabel ? undefined : ariaHidden}
    aria-label={ariaLabel}
    role={ariaLabel ? 'img' : undefined}
    {...props}
  >
    {ICON_PATHS[name]}
  </svg>
)

Icon.displayName = 'Icon'
export default Icon