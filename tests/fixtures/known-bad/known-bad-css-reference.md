# Known-bad css reference

Fixture for tests/validate_reference_css.py. Never referenced by the shipped
skill — it exists so tests/run.sh can prove the validator still rejects both
of its failure modes after a refactor.

## Valid fence (must be accepted on its own)

```css
.known-bad-ok {
  display: flex;
  gap: 0.5rem;
}
```

## Malformed css fence (stray closing brace)

```css
.known-bad-malformed {
  color: red;
}
}
```

## scss fence (rejected for being scss, not for parsing)

```scss
.known-bad-scss {
  color: red;

  &:hover {
    color: blue;
  }
}
```
