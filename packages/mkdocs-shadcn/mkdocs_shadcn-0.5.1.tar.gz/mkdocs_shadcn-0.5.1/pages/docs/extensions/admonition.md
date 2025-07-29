---
title: Admonitions
summary: Notes, infos, warnings and dangers
---

The Admonition extension adds rST-style admonitions to Markdown documents.

## Configuration

```yaml
# mkdocs.yml

markdown_extensions:
  - admonition
```

## Syntax

    :::md {.light}
    !!! info "Information:"
        Something **new** is coming to `mkdocs-shadcn`

    !!! note "Note:"
        We notice that `x=2`

    !!! warning "Warning:"
        There is a *risk* doing `x/0`

    !!! danger "Danger:"
        Don't look at `node_modules` **please**! 


!!! info "Information:"
    Something **new** is coming to `mkdocs-shadcn`

!!! note "Note:"
    We notice that `x=2`

!!! warning "Warning:"
    There is a *risk* doing `x/0`

!!! danger "Danger:"
    Don't look at `node_modules` **please**! 