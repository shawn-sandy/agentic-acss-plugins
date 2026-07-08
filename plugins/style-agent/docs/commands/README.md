# style-agent commands — Usage Guides

Consumer usage guides for the three CSS commands shipped by `style-agent`. Each guide covers when to reach for the command, how to run it, a copy-paste before/after example, and important behavior.

| Command | What it does | Guide |
|---|---|---|
| `/css-to-class [name]` | Collapse a utility class list (or HTML element) into one named CSS class, resolving declarations from your project's `.css` files. | [css-to-class.md](css-to-class.md) |
| `/inline-style-to-class [name]` | Convert an inline style attribute, JSX style object, or `<style>` block into a named class appended to your stylesheet, tokenizing values into CSS variables. | [inline-style-to-class.md](inline-style-to-class.md) |
| `/create-utilities [description]` | Generate a utility class string from a plain-language visual description, matched to your project's framework. | [create-utilities.md](create-utilities.md) |

See the [style-agent developer guide](../README.md) for plugin internals and skill layout.
