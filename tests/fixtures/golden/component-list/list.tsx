export type ListType = 'ul' | 'ol' | 'dl'

export type ListProps = {
  /** List variant: ul | ol | dl (default: ul) */
  type?: ListType
  /** Visual variant — drives data-variant for SCSS targeting */
  variant?: 'inline' | 'numbered' | 'none' | string
  /**
   * Explicit role override.
   * Pass `role="list"` when applying `variant="none"` (or any unstyled variant)
   * to restore list semantics for VoiceOver/Safari, which strip them when
   * `list-style: none` is applied via CSS.
   */
  role?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'ul'>, 'type'>

export type ListItemType = 'li' | 'dt' | 'dd'

export type ListItemProps = {
  /** li (default), dt, or dd — match the parent list type */
  type?: ListItemType
  id?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'li'>, 'type'>

import UI from '../ui'
import React from 'react'

export type ListType = 'ul' | 'ol' | 'dl'


export type ListItemType = 'li' | 'dt' | 'dd'


const ListItem = React.forwardRef<HTMLLIElement | HTMLElement, ListItemProps>(
  ({ type = 'li', id, styles, children, classes, ...props }, ref) => (
    <UI
      id={id}
      as={type}
      className={classes}
      style={styles}
      ref={ref}
      {...props}
    >
      {children}
    </UI>
  ),
)
ListItem.displayName = 'ListItem'

const ListRoot = React.forwardRef<
  HTMLUListElement | HTMLOListElement | HTMLDListElement,
  ListProps
>(({ children, classes, type = 'ul', variant, styles, role, ...props }, ref) => (
  <UI
    as={type}
    data-variant={variant}
    className={classes}
    style={styles}
    role={role}
    ref={ref}
    {...props}
  >
    {children}
  </UI>
))
ListRoot.displayName = 'List'

type ListComponent = typeof ListRoot & {
  ListItem: typeof ListItem
}

export const List = Object.assign(ListRoot, { ListItem }) as ListComponent

export default List