export type InputValidationState = 'none' | 'valid' | 'invalid'

export type InputProps = {
  /** Required for label association and aria-describedby id generation */
  id: string
  /** HTML input type (default: 'text') */
  type?: React.HTMLInputTypeAttribute
  /** Form field name */
  name?: string
  /** Controlled value */
  value?: string | number | readonly string[]
  /** Uncontrolled initial value */
  defaultValue?: string | number | readonly string[]
  /** Placeholder text */
  placeholder?: string
  /** Inline styles */
  styles?: React.CSSProperties
  /** Custom CSS classes */
  classes?: string
  /** Accessible disabled (aria-disabled pattern; keeps element focusable) */
  disabled?: boolean
  /** Legacy alias for `disabled` — `disabled` takes precedence */
  isDisabled?: boolean
  /** Read-only state */
  readOnly?: boolean
  /** Required for submission and screen readers */
  required?: boolean
  /** Validation state — drives aria-invalid and the data-validation attribute */
  validationState?: InputValidationState
  /** Error message rendered by the parent and linked via aria-describedby */
  errorMessage?: string
  /** Hint / helper text linked via aria-describedby */
  hintText?: string
  /** Native change handler */
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  /** Blur handler */
  onBlur?: React.FocusEventHandler<HTMLInputElement>
  /** Focus handler — NOT gated by disabled state (intentional) */
  onFocus?: React.FocusEventHandler<HTMLInputElement>
  /** Key-down handler */
  onKeyDown?: React.KeyboardEventHandler<HTMLInputElement>
  /** Convenience handler for Enter — fires after onKeyDown */
  onEnter?: React.KeyboardEventHandler<HTMLInputElement>
  maxLength?: number
  minLength?: number
  pattern?: string
  autoComplete?: string
  autoFocus?: boolean
  inputMode?: 'text' | 'numeric' | 'decimal' | 'tel' | 'email' | 'url' | 'search' | 'none'
} & Omit<React.ComponentPropsWithoutRef<'input'>, 'id' | 'disabled' | 'value' | 'defaultValue' | 'onChange' | 'onBlur' | 'onFocus' | 'onKeyDown'>

import UI from '../ui'
import React from 'react'

const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false

function useDisabledState<T extends HTMLElement = HTMLInputElement>(
  disabled: boolean | undefined,
  handlers: {
    onChange?: (e: React.ChangeEvent<T>) => void
    onKeyDown?: (e: React.KeyboardEvent<T>) => void
    onBlur?: (e: React.FocusEvent<T>) => void
  } = {},
  className?: string,
) {
  const isDisabled = Boolean(disabled)
  const merged = [isDisabled ? 'is-disabled' : '', className]
    .filter(Boolean).join(' ')
  const wrap = <E,>(fn?: (e: E) => void) => fn
    ? (e: any) => { if (isDisabled) { e.preventDefault(); e.stopPropagation(); return } fn(e) }
    : undefined

  return {
    disabledProps: { 'aria-disabled': isDisabled, className: merged },
    handlers: {
      onChange: wrap(handlers.onChange),
      onKeyDown: wrap(handlers.onKeyDown),
      onBlur: wrap(handlers.onBlur),
    },
  }
}


export const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  type = 'text',
  name,
  value,
  defaultValue,
  placeholder,
  id,
  styles,
  classes,
  isDisabled,
  disabled,
  readOnly,
  required = false,
  validationState = 'none',
  errorMessage,
  hintText,
  onChange,
  onBlur,
  onFocus,
  onKeyDown,
  onEnter,
  maxLength,
  minLength,
  pattern,
  autoComplete,
  autoFocus = false,
  inputMode,
  ...props
}: InputProps, ref) => {
  const isInputDisabled = resolveDisabledState(disabled, isDisabled)

  const { disabledProps, handlers } = useDisabledState<HTMLInputElement>(
    isInputDisabled,
    {
      onChange,
      onBlur,
      onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && onEnter) onEnter(e)
        onKeyDown?.(e)
      },
    },
    classes,
  )

  const isInvalid = validationState === 'invalid'

  const describedByIds: string[] = []
  if (errorMessage && id) describedByIds.push(`${id}-error`)
  if (hintText && id) describedByIds.push(`${id}-hint`)
  const ariaDescribedBy = describedByIds.length > 0 ? describedByIds.join(' ') : undefined

  return (
    <UI
      as="input"
      ref={ref}
      id={id}
      type={type}
      name={name}
      value={value}
      defaultValue={defaultValue}
      placeholder={placeholder}
      className={disabledProps.className}
      styles={styles}
      readOnly={readOnly}
      required={required}
      maxLength={maxLength}
      minLength={minLength}
      pattern={pattern}
      autoComplete={autoComplete}
      autoFocus={autoFocus}
      inputMode={inputMode}
      {...handlers}
      onFocus={onFocus}
      aria-disabled={disabledProps['aria-disabled']}
      aria-readonly={readOnly}
      aria-required={required}
      aria-invalid={isInvalid}
      aria-describedby={ariaDescribedBy}
      data-validation={validationState}
      {...props}
    />
  )
})

Input.displayName = 'Input'
export default Input