# Design Exploration Protocol

Fallback protocol for generating design variants inline when gstack-design-shotgun
is unavailable. Uses DESIGN.md constraints to produce structured alternatives.

## When to Use

- gstack-design-shotgun skill is not installed or not reachable
- Quick design exploration needed without external tooling
- User wants to compare directions before committing to implementation

## Step 1: Read DESIGN.md Constraints

1. Load existing DESIGN.md (required — abort if missing)
2. Extract: aesthetic direction, color palette, typography stack, layout approach
3. Identify which dimensions have room for variation vs which are locked

## Step 2: Generate 2-3 Design Variants

For each variant, produce:

| Section | Content |
|---------|---------|
| Visual direction | One-sentence mood description |
| Color palette | Primary, secondary, accent, neutrals (hex values) |
| Typography choices | Display font, body font, data font with rationale |
| Layout approach | Grid structure, density, key compositional decisions |
| Differentiation | What makes this variant distinct from the others |

### Variant Generation Rules

- Variant A: closest to current DESIGN.md (safe evolution)
- Variant B: push one dimension further (bolder color, different aesthetic)
- Variant C (optional): challenge an assumption (different layout, unexpected font)
- All variants must respect locked constraints from DESIGN.md
- Each variant must be internally coherent (font + color + layout reinforce each other)

## Step 3: Structured Comparison

Present variants side-by-side:

```
VARIANT A: [name]          VARIANT B: [name]          VARIANT C: [name]
Direction: ...             Direction: ...             Direction: ...
Palette: ...               Palette: ...               Palette: ...
Typography: ...            Typography: ...            Typography: ...
Layout: ...                Layout: ...                Layout: ...
Best for: ...              Best for: ...              Best for: ...
Risk level: low            Risk level: medium         Risk level: high
```

Ask user: "Which direction resonates? You can also mix elements across variants."

## Step 4: Apply Chosen Direction

1. Confirm final selections (may be a mix of elements from multiple variants)
2. Update DESIGN.md with the chosen direction
3. Document the decision in the Decisions Log section
4. If implementation is next, hand off to dev-code with the updated DESIGN.md
