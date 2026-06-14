export type CardProps = {
  /** HTML element to render as (default: div) */
  as?: React.ElementType
  /** Card content */
  children?: React.ReactNode
  /** Enable keyboard/mouse click for the whole card */
  interactive?: boolean
  /** Click handler (required when interactive=true) */
  onClick?: () => void
  /** CSS class names */
  classes?: string
  /** Inline styles */
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'div'>, 'onClick'>

type CardTitleProps = {
  /** HTML element to render as (default: h3) */
  as?: React.ElementType
  children?: React.ReactNode
  className?: string
  id?: string
} & React.ComponentPropsWithoutRef<'h3'>

type CardContentProps = {
  /** HTML element to render as (default: article) */
  as?: React.ElementType
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'article'>

type CardFooterProps = {
  /** HTML element to render as (default: div) */
  as?: React.ElementType
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'div'>

import UI from '../ui'
import React from 'react'

// --- Sub-components ---
const CardTitle = ({
  as = 'h3',
  children,
  className,
  id,
  ...props
}: CardTitleProps) => (
  <UI as={as} classes={`card-title${className ? ' ' + className : ''}`} id={id} {...props}>
    {children}
  </UI>
)
CardTitle.displayName = 'Card.Title'

const CardContent = ({
  as = 'article',
  children,
  ...props
}: CardContentProps) => (
  <UI as={as} classes="card-content" {...props}>
    {children}
  </UI>
)
CardContent.displayName = 'Card.Content'

const CardFooter = ({
  as = 'div',
  children,
  ...props
}: CardFooterProps) => (
  <UI as={as} classes="card-footer" {...props}>
    {children}
  </UI>
)
CardFooter.displayName = 'Card.Footer'

// --- Root component ---
const CardRoot = ({
  as = 'div',
  children,
  interactive,
  onClick,
  classes,
  styles,
  ...props
}: CardProps) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (interactive && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault()
      onClick?.()
    }
  }

  return (
    <UI
      as={as}
      classes={`card${classes ? ' ' + classes : ''}`}
      styles={styles}
      data-card={interactive ? 'interactive' : undefined}
      role={interactive ? 'button' : undefined}
      tabIndex={interactive ? 0 : undefined}
      onClick={interactive ? onClick : undefined}
      onKeyDown={interactive ? handleKeyDown : undefined}
      {...props}
    >
      {children}
    </UI>
  )
}
CardRoot.displayName = 'Card'

// --- Compound assembly ---
type CardComponent = typeof CardRoot & {
  Title: typeof CardTitle
  Content: typeof CardContent
  Footer: typeof CardFooter
}

export const Card = Object.assign(CardRoot, {
  Title: CardTitle,
  Content: CardContent,
  Footer: CardFooter,
}) as CardComponent

export default Card