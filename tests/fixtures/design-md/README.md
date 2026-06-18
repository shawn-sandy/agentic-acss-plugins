# DESIGN.md dogfood fixture

[`DESIGN.md`](./DESIGN.md) is acss-kit's own default theme, published as a
[Google Labs DESIGN.md](https://github.com/google-labs-code/design.md) through
the real `/design-export` pipeline. It pairs with the 15
`plugins/acss-kit/skills/component-*/*.component.md` files: together they are the
two-file design system (DESIGN.md owns tokens, COMPONENT.md owns components),
and this fixture is here so the two halves are verified to actually fit.

`tests/run.sh` **step 7g** asserts:

1. **Resolution** — every `{colors|spacing|rounded|typography}.*` reference in
   the component files resolves to a token defined in this DESIGN.md's
   front-matter. (This is what caught the original vocabulary drift: components
   referenced acss-kit role names like `colors.text` while the exporter emits the
   DESIGN.md/M3 name `colors.on-surface`.)
2. **Closed loop** — re-importing this DESIGN.md's colors through
   `design_md_to_tokens.py` → `tokens_to_css.py` still passes the WCAG contrast
   gate (`validate_theme.py`).

## Regenerate

The front-matter is machine-generated, with one hand-added token
(`surface-container-low` — the default palette omits the optional
`--color-surface-subtle` role that `component-table`'s header reads). The prose
body (Overview, the human-readable tables, Components) is hand-maintained. To
refresh the tokens:

```sh
S=plugins/acss-kit/scripts
TMP=$(mktemp -d)
python3 $S/generate_palette.py "#4f46e5" > "$TMP/palette.json"
python3 $S/tokens_to_css.py "$TMP/palette.json" --out-dir="$TMP"
cp plugins/acss-kit/assets/tokens/space-radius.css \
   plugins/acss-kit/assets/tokens/typography.css "$TMP/"
python3 $S/tokens_to_design_md.py --dir="$TMP" --name="acss-kit"
```

Copy the emitted YAML front-matter (everything through the closing `---`) over
the top of `DESIGN.md`, keeping the prose body below it. The seed is `#4f46e5`
(the README quickstart's indigo); change it to rebrand the dogfood theme.
