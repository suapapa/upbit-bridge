# Upbit Bridge — Product Context

## Register

**brand** — `site/` is a marketing landing page. Design is the deliverable; visitors should understand the product and start using it.

## Users & Purpose

- **Who:** Developers running AI coding assistants (Cursor, Claude Desktop) or scripts/bots who trade or analyze crypto on Upbit.
- **Job:** Connect Upbit OpenAPI to MCP clients and REST/WebSocket consumers without writing custom glue code.
- **Outcome:** Clone the repo, run Docker, paste MCP config or call `/api/v1/`, stream `/ws/`.

## Brand Personality

Precise · Terminal-native · Trustworthy

Not playful crypto hype. Reads like infrastructure docs with a clear visual voice.

## Anti-References

- Generic SaaS hero metrics (big numbers + small labels)
- Purple-gold fintech gradient clichés
- Identical icon-card grids on every section
- Uppercase tracked eyebrows above every heading
- Glassmorphism headers and decorative blur

## Strategic Design Principles

1. Show the product (terminal output, MCP config snippets) before listing features.
2. One accent color (gold) on a dark slate base; purple only for code highlights.
3. Korean copy, natural tone; no AI filler words.
4. Mobile navigation must reach every section.
5. Accessibility: WCAG AA contrast, keyboard focus, reduced motion.

## Accessibility

- WCAG 2.1 AA minimum
- Korean primary language (`lang="ko"`)
- Code and brand names marked `translate="no"`
