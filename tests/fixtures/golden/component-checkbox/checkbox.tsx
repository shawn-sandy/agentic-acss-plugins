export interface CheckboxProps extends Omit<
  InputProps,
  'type' | 'value' | 'onChange' | 'defaultValue' | 'placeholder'
> {
  /** Required for label association */
  id: string
  /** Visible label text */
  label: React.ReactNode
  /** Size preset (default: 'md') */
  size?: 'xs' | 'sm' | 'md' | 'lg'
  /** Controlled checked state */
  checked?: boolean
  /** Uncontrolled initial state */
  defaultChecked?: boolean
  /** Form-submission value when checked (default: 'on') */
  value?: string
  /** Boolean change handler — receives true/false, not a ChangeEvent */
  onChange?: (checked: boolean) => void
  /** Wrapper div CSS classes */
  classes?: string
  /** Input element CSS classes (default: 'checkbox-input') */
  inputClasses?: string
  /** CSS custom properties for theming / custom sizing */
  styles?: React.CSSProperties
}

import React from 'react'
import Input, { type InputProps } from '../input/input'

export interface CheckboxProps extends Omit<
  InputProps,
  'type' | 'value' | 'onChange' | 'defaultValue' | 'placeholder'
> {
  id: string
  label: React.ReactNode
  size?: 'xs' | 'sm' | 'md' | 'lg'
  checked?: boolean
  defaultChecked?: boolean
  value?: string
  onChange?: (checked: boolean) => void
  classes?: string
  inputClasses?: string
  styles?: React.CSSProperties
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(({
  id,
  label,
  checked,
  defaultChecked,
  value = 'on',
  onChange,
  classes,
  inputClasses,
  styles,
  size,
  name,
  disabled,
  required,
  validationState,
  errorMessage,
  hintText,
  onBlur,
  onFocus,
  autoFocus,
  ...props
}, ref) => {
  // Adapt boolean onChange to native ChangeEvent
  const handleChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e.target.checked)
    },
    [onChange],
  )

  const isControlled = checked !== undefined
  const checkedProp = isControlled ? { checked } : {}
  const defaultCheckedProp = !isControlled && defaultChecked !== undefined
    ? { defaultChecked }
    : {}

  // Dev-only: warn on controlled <-> uncontrolled mode flip.
  const wasControlledRef = React.useRef(isControlled)
  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      if (wasControlledRef.current !== isControlled) {
        // eslint-disable-next-line no-console
        console.warn(
          `Checkbox id="${id}" is changing from ${wasControlledRef.current ? 'controlled' : 'uncontrolled'} to ${isControlled ? 'controlled' : 'uncontrolled'}. Pick one and stick with it.`,
        )
      }
      wasControlledRef.current = isControlled
    }
  }, [isControlled, id])

  return (
    <div className={classes} style={styles} data-checkbox-size={size}>
      <Input
        ref={ref}
        type="checkbox"
        id={id}
        name={name}
        value={value}
        {...checkedProp}
        {...defaultCheckedProp}
        classes={inputClasses || 'checkbox-input'}
        disabled={disabled}
        required={required}
        validationState={validationState}
        errorMessage={errorMessage}
        hintText={hintText}
        onChange={handleChange}
        onBlur={onBlur}
        onFocus={onFocus}
        autoFocus={autoFocus}
        {...props}
      />
      <label htmlFor={id} className="checkbox-label">
        {label}
        {required && (
          <span className="checkbox-required" aria-label="required">{' *'}</span>
        )}
      </label>
    </div>
  )
})

Checkbox.displayName = 'Checkbox'
export default Checkbox