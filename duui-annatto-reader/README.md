# Annatto Reader Documentation

## Overview

The **Annatto Reader** requires an additional `.toml` configuration file included in the target corpora `.zip` file. This `.toml` file contains critical configuration data necessary for Annatto to function correctly. Without it, the Annatto Reader cannot process the corpus.

**Key Requirement**: Each `.zip` file must contain exactly **one** `.toml` file.

## TOML Configuration Details

For detailed information about the `.toml` file format and specifications, refer to the official documentation [here](https://github.com/korpling/annatto/tree/v0.27.1).

### Placeholders

In the `import` and `export` sections of the `.toml` file, the import and export paths must be replaced with the following placeholders:

- **{{IMPORT}}**: Placeholder for the import path.
- **{{EXPORT}}**: Placeholder for the export path.

### Export Format

The export format must always be set to **CoNLL-U** (`conllu`).

### Example TOML Configuration

Below is an example `.toml` template for the Annatto Reader:

```toml
[[import]]
format = "relannis"
path = "{{IMPORT}}"
[import.config]

[[export]]
path = "{{EXPORT}}"
format = "conllu"

[export.config]
ordering = { ctype = "Ordering", layer = "default_ns", name = "text" }
form = { ns = "default_ns", name = "text" }
lemma = { ns = "default_ns", name = "lemma" }
upos = { ns = "default_ns", name = "pos" }
```

## Notes

- Ensure the `.toml` file is correctly formatted and included in the `.zip` file alongside the corpus data.
- The placeholders `{{IMPORT}}` and `{{EXPORT}}` will be replaced with actual paths during processing (e.g., using a Python script as described in related workflows).
- The `export.config` section specifies mappings for linguistic annotations (e.g., `form`, `lemma`, `upos`) to the `default_ns` namespace.
