export type LinkProps = {
  /** Required href */
  href: string
  /** Link target (e.g. "_blank") */
  target?: string
  /** rel tokens — merged with security defaults when target="_blank" */
  rel?: string
  /** Whether to add a prefetch hint (default: false) */
  prefetch?: boolean
  /** Maps to data-btn attribute for button-style links */
  btnStyle?: string
  /** Inline styles */
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'a'>, 'href' | 'target' | 'rel'>

import UI from '../ui'
import React from 'react'


export const Link = React.forwardRef<HTMLAnchorElement, LinkProps>(
  (
    {
      href,
      target,
      rel,
      children,
      styles,
      prefetch = false,
      btnStyle,
      onClick,
      onPointerDown,
      ...props
    },
    ref,
  ) => {
    const computedRel = React.useMemo(() => {
      if (target === '_blank') {
        const tokens = new Set(['noopener', 'noreferrer'])
        if (prefetch) tokens.add('prefetch')
        if (rel) {
          rel.split(/\s+/).forEach((t) => { if (t) tokens.add(t) })
        }
        return Array.from(tokens).join(' ')
      }
      return rel
    }, [target, rel, prefetch])

    return (
      <UI
        as="a"
        ref={ref}
        href={href}
        target={target}
        rel={computedRel}
        styles={styles}
        data-btn={btnStyle}
        onClick={onClick}
        onPointerDown={onPointerDown}
        {...props}
      >
        {children}
      </UI>
    )
  },
)

Link.displayName = 'Link'
export default Link