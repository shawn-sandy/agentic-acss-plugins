export type TableProps = {
  /** Optional accessible name for the table — alternative to <caption> */
  'aria-label'?: string
  /** Optional accessible name reference — alternative to <caption> */
  'aria-labelledby'?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'table'>

export type TableCaptionProps = React.ComponentPropsWithoutRef<'caption'>
export type TableHeadProps = React.ComponentPropsWithoutRef<'thead'>
export type TableBodyProps = React.ComponentPropsWithoutRef<'tbody'>
export type TableRowProps = React.ComponentPropsWithoutRef<'tr'>
export type TableHeaderCellProps = React.ComponentPropsWithoutRef<'th'> & {
  /** Required when scope cannot be inferred from position */
  scope?: 'col' | 'row' | 'colgroup' | 'rowgroup'
}
export type TableCellProps = React.ComponentPropsWithoutRef<'td'>

import UI from '../ui'
import React from 'react'

const TableCaption = ({ children, ...props }: TableCaptionProps) => (
  <UI as="caption" {...props}>{children}</UI>
)
TableCaption.displayName = 'Table.Caption'

const TableHead = ({ children, ...props }: TableHeadProps) => (
  <UI as="thead" {...props}>{children}</UI>
)
TableHead.displayName = 'Table.Head'

const TableBody = ({ children, ...props }: TableBodyProps) => (
  <UI as="tbody" {...props}>{children}</UI>
)
TableBody.displayName = 'Table.Body'

const TableRow = ({ children, ...props }: TableRowProps) => (
  <UI as="tr" {...props}>{children}</UI>
)
TableRow.displayName = 'Table.Row'

const TableHeaderCell = ({ scope = 'col', children, ...props }: TableHeaderCellProps) => (
  <UI as="th" scope={scope} {...props}>{children}</UI>
)
TableHeaderCell.displayName = 'Table.HeaderCell'

const TableCell = ({ children, ...props }: TableCellProps) => (
  <UI as="td" {...props}>{children}</UI>
)
TableCell.displayName = 'Table.Cell'

const TableRoot = ({ classes, styles, children, ...props }: TableProps) => (
  <UI
    as="table"
    classes={`table${classes ? ' ' + classes : ''}`}
    styles={styles}
    {...props}
  >
    {children}
  </UI>
)
TableRoot.displayName = 'Table'

type TableComponent = typeof TableRoot & {
  Caption: typeof TableCaption
  Head: typeof TableHead
  Body: typeof TableBody
  Row: typeof TableRow
  HeaderCell: typeof TableHeaderCell
  Cell: typeof TableCell
}

export const Table = Object.assign(TableRoot, {
  Caption: TableCaption,
  Head: TableHead,
  Body: TableBody,
  Row: TableRow,
  HeaderCell: TableHeaderCell,
  Cell: TableCell,
}) as TableComponent

export default Table