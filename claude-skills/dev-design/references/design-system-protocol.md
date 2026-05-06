# Design System Protocol

Reference for gstack-design-consultation design system creation workflow.

## Purpose

Understand the product, research the landscape, propose a complete design system
(aesthetic, typography, color, layout, spacing, motion), and generate font+color
preview pages. Creates DESIGN.md as the project's design source of truth.

## Phase 1: Product Understanding

1. Check for existing DESIGN.md — offer update, fresh start, or cancel
2. Gather product context from codebase (README, package.json, directory structure)
3. Check for office-hours output (pre-filled product context)
4. Ask single comprehensive question covering:
   - Product identity, target users, space/industry
   - Project type (web app, dashboard, marketing site, editorial, internal tool)
   - Research preference (competitive research or work from design knowledge)
5. Memorable-thing forcing question: "What's the one thing you want someone to
   remember after seeing this product for the first time?"

## Phase 2: Landscape Research (if requested)

1. WebSearch for 5-10 products in the space
2. Visual research via browse (if available): visit top 3-5 sites, capture screenshots
3. Three-layer synthesis:
   - Layer 1 (tried and true): patterns every product shares (table stakes)
   - Layer 2 (new and popular): trending patterns, emerging approaches
   - Layer 3 (first principles): where conventional approach is wrong for THIS product

## Phase 3: Design System Proposal Structure

Present as one coherent package with SAFE/RISK breakdown:

| Dimension | Content |
|-----------|---------|
| Aesthetic | Direction name + rationale |
| Decoration | Level (minimal/intentional/expressive) + pairing rationale |
| Layout | Approach (grid-disciplined/creative-editorial/hybrid) + fit rationale |
| Color | Approach + proposed palette (hex values) + rationale |
| Typography | 3 font recommendations with roles + rationale |
| Spacing | Base unit + density + rationale |
| Motion | Approach + rationale |

### SAFE/RISK Breakdown

- SAFE choices: 2-3 decisions matching category conventions (table stakes)
- RISKS: 2-3 deliberate departures from convention, each with:
  - What it is
  - Why it works
  - What you gain
  - What it costs

## Font and Color Guidelines

### Font Recommendations by Purpose

| Purpose | Candidates |
|---------|-----------|
| Display/Hero | Satoshi, General Sans, Instrument Serif, Fraunces, Clash Grotesk, Cabinet Grotesk |
| Body | Instrument Sans, DM Sans, Source Sans 3, Geist, Plus Jakarta Sans, Outfit |
| Data/Tables | Geist (tabular-nums), DM Sans (tabular-nums), JetBrains Mono, IBM Plex Mono |
| Code | JetBrains Mono, Fira Code, Berkeley Mono, Geist Mono |

### Never Recommend (blacklist)

Papyrus, Comic Sans, Lobster, Impact, Jokerman, Bleeding Cowboys, Permanent Marker,
Bradley Hand, Brush Script, Hobo, Trajan, Raleway, Clash Display, Courier New (body)

### Overused (only if user specifically requests)

Inter, Roboto, Arial, Helvetica, Open Sans, Lato, Montserrat, Poppins, Space Grotesk

## Phase 5: Preview Generation

### Path A: AI Mockups (if design binary available)

1. Generate 3 variants with `$D variants --brief "..." --count 3`
2. Quality-gate each variant (reject AI slop patterns)
3. Create comparison board with `$D compare --images "..." --serve`
4. Collect feedback via board UI or AskUserQuestion
5. Extract design tokens from approved variant with `$D extract`

### Path B: HTML Preview (fallback)

Generate self-contained HTML file with:
- Proposed fonts loaded from Google/Bunny Fonts
- Color palette swatches with hex values
- Font specimen section (each font in its proposed role)
- Realistic product mockups matching project type
- Light/dark mode toggle
- Responsive layout

## DESIGN.md Template

```markdown
# Design System -- [Project Name]

## Product Context
## Aesthetic Direction
## Typography
## Color
## Spacing
## Layout
## Motion
## Decisions Log
```

## Coherence Validation Rules

Flag mismatches when user overrides one section:
- Brutalist aesthetic + expressive motion -> unusual pairing, confirm intent
- Expressive color + restrained decoration -> colors carry heavy weight
- Creative-editorial layout + data-heavy product -> may fight density

Always accept user's final choice. Nudge, never block.
