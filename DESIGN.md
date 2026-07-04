---
name: Upbit Bridge
description: Dark developer landing for Upbit MCP gateway
colors:
  background: "#0f172a"
  surface: "#1e293b"
  surface-muted: "#272f42"
  foreground: "#f8fafc"
  muted-foreground: "#b4c0cf"
  primary: "#f59e0b"
  primary-hover: "#fbbf24"
  on-primary: "#0f172a"
  accent: "#8b5cf6"
  accent-hover: "#7c3aed"
  on-accent: "#ffffff"
  border: "#334155"
  destructive: "#ef4444"
  destructive-muted: "#fca5a5"
typography:
  display:
    fontFamily: "Orbitron, system-ui, sans-serif"
    fontSize: "clamp(2.25rem, 6vw, 4rem)"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.03em"
  body:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  mono:
    fontFamily: "ui-monospace, Cascadia Code, Source Code Pro, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
rounded:
  sm: "0.375rem"
  md: "0.5rem"
  lg: "0.75rem"
  xl: "1rem"
spacing:
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
  section: "4rem"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "0 1.5rem"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "0 1.5rem"
  button-accent:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    rounded: "{rounded.md}"
    padding: "0 1.5rem"
---

# Design System

## Overview

Dark, terminal-native landing page for a developer tool. Gold signals action; slate carries structure; purple appears only in accents and code. Restrained motion, no glass effects.

## Colors

| Role | Token | Usage |
|------|-------|-------|
| Page bg | `background` | Body, terminal blocks |
| Cards | `surface` | Bento cells, panels |
| Alt sections | `surface-muted` | Alternating bands |
| Body text | `foreground` | Headings, primary copy |
| Secondary | `muted-foreground` | Descriptions (AA on dark surfaces) |
| CTA | `primary` | Primary buttons, highlights |
| Code accent | `accent` | Secondary CTA, step numbers |

Body text on `surface-muted` must use `muted-foreground` (#b4c0cf) or brighter, never slate-400.

## Typography

- **Display:** Orbitron for h1–h2 and logo only.
- **Body:** Source Sans 3 for everything else.
- **Mono:** System monospace for code, tool names, terminal output.

## Layout

- Max content width: 72rem.
- Section padding: 4rem block.
- Bento grids use asymmetric spans, not uniform 3-column card rows.
- `scroll-margin-top: 5rem` on anchored sections (sticky header clearance).

## Components

- Buttons: 44px min height, visible `:focus-visible` ring.
- Terminal panel: dark inset surface, monospace, no images required.
- Mobile nav: `<details>` drawer below 768px; desktop inline links.

## Motion

- Transitions: 150–200ms ease-out on color, border, transform only.
- `prefers-reduced-motion: reduce` disables transitions globally.

## Sidecar (non-Stitch tokens)

```yaml
z-index:
  sticky: 50
  skip-link: 100
focus-ring: "2px solid #f59e0b"
header-height: 4rem
```
