export type FieldProps = {
  /** Label content — accepts text or a React node */
  label: React.ReactNode
  /**
   * REQUIRED — must match the `id` of the wrapped control.
   * The type makes the value required; runtime can't enforce that the wrapped control
   * actually has a matching `id`, so authoring discipline matters here.
   */
  labelFor: string
  /** The form control rendered inside (Input, Select, Textarea, etc.) */
  children: React.ReactNode
  /** Optional id on the wrapper div */
  id?: string
  classes?: string
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'label'>, 'htmlFor'>

import UI from '../ui'
import React from 'react'


export const Field = ({
  label,
  labelFor,
  id,
  styles,
  classes,
  children,
  ...props
}: FieldProps) => (
  <UI
    as="div"
    id={id}
    styles={styles}
    classes={classes}
    data-style="fields"
    {...props}
  >
    <label htmlFor={labelFor}>{label}</label>
    {children}
  </UI>
)

Field.displayName = 'Field'
export default Field