# pre-commit-fluent-hook

A pre-commit hook for validating Fluent (FTL) files.

## Installation

```bash
pip install pre-commit-fluent-hook
```

## Usage

Add this to your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/uutils/pre-commit-fluent-hook
    rev: v.0.0.1
    hooks:
    -   id: check-fluent
```

## What it does

The `check-fluent` hook validates Fluent (FTL) files by checking:

- Message identifier naming conventions (must start with letter, can contain letters, numbers, underscores, and hyphens)
- Attribute identifier naming conventions
- Proper indentation for attributes and variants
- Select expressions have default variants (marked with `*`)
- Variants are only used within select expressions
- File encoding (UTF-8)

## Example

Given a file `messages.ftl`:

```fluent
# Valid
hello = Hello, world!
greeting = Hello, { $name }!
    .title = Greeting

# Invalid - missing default variant
emails = { $unreadEmails ->
    [0] You have no unread emails.
    [one] You have one unread email.
}
```

The hook will report the missing default variant error.
