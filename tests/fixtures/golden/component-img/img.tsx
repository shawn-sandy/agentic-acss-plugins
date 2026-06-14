export type ImgProps = {
  /** Image source URL */
  src?: string
  /** Required alt text — empty string for decorative images */
  alt: string
  /** Image width (number = px) */
  width?: number | string
  /** Image height (number = px). Defaults to "auto" if width is set. */
  height?: number | string
  /** Inline styles */
  styles?: React.CSSProperties
  /** Loading strategy — "lazy" by default for below-the-fold images */
  loading?: 'lazy' | 'eager'
  /** Custom fallback URL when src fails to load. Defaults to a generated SVG. */
  placeholder?: string
  /** Fetch priority hint */
  fetchpriority?: 'high' | 'low' | 'auto'
  /** Decoding strategy */
  decoding?: 'sync' | 'async' | 'auto'
  /** Responsive image candidates */
  srcSet?: string
  /** Responsive sizes hint */
  sizes?: string
  /** Custom error handler — call e.preventDefault() to skip the placeholder */
  onError?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void
  onLoad?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void
} & Omit<React.ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt' | 'onError' | 'onLoad'>

import UI from '../ui'
import React, { useMemo } from 'react'


export const Img = ({
  src = '//',
  alt,
  width = 480,
  height,
  styles,
  loading = 'lazy',
  placeholder,
  fetchpriority = 'low',
  decoding = 'auto',
  srcSet,
  sizes,
  onError,
  onLoad,
  ...props
}: ImgProps) => {
  // Generated SVG-gradient placeholder — memoized, zero network requests.
  const defaultPlaceholder = useMemo(() => {
    const w = typeof width === 'number' ? width : 480
    const h = typeof height === 'number' ? height : Math.round(w * 0.75)
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}">
      <defs>
        <linearGradient id="grad-${w}-${h}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#6366f1"/>
          <stop offset="50%" style="stop-color:#8b5cf6"/>
          <stop offset="100%" style="stop-color:#ec4899"/>
        </linearGradient>
      </defs>
      <rect width="${w}" height="${h}" fill="url(#grad-${w}-${h})"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="system-ui,-apple-system,sans-serif"
            font-size="${Math.max(16, Math.min(w, h) * 0.05)}"
            font-weight="500" fill="rgba(255,255,255,0.9)">${w}×${h}</text>
    </svg>`
    return `data:image/svg+xml,${encodeURIComponent(svg)}`
  }, [width, height])

  const fallbackPlaceholder = placeholder ?? defaultPlaceholder

  const handleImgError = (e: React.SyntheticEvent<HTMLImageElement, Event>): void => {
    onError?.(e)
    if (!e.defaultPrevented && e.currentTarget.src !== fallbackPlaceholder) {
      e.currentTarget.src = fallbackPlaceholder
    }
  }

  const handleImgLoad = (e: React.SyntheticEvent<HTMLImageElement, Event>): void => {
    onLoad?.(e)
  }

  return (
    <UI
      as="img"
      src={src}
      alt={alt}
      width={width}
      height={height || 'auto'}
      loading={loading}
      style={styles}
      srcSet={srcSet}
      sizes={sizes}
      onError={handleImgError}
      onLoad={handleImgLoad}
      decoding={decoding}
      {...props}
      {...(fetchpriority && { fetchpriority })}
    />
  )
}

Img.displayName = 'Img'
export default Img