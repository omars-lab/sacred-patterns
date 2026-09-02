# Iteration 7 Guidance

## Primary Target: Satellite Isolation

The biggest visual gap is that satellite rosettes merge into one connected web. The reference shows 10 clearly distinct mini-stars.

## Approach: Reduce Satellite Radius

Try making ring-1 circles smaller so their hankin rays don't overlap with adjacent satellites.

```
repeat at C0 depth 1
    circle center($point) radius 0.7 * $radius
    divide into 10
```

If `0.7 * $radius` is not supported as an expression, try:
- `radius 70` (hardcoded — acceptable for experimentation)
- Or use a DSL variable if available

## Fallback: Per-Sector Explicit Construction

If reducing radius doesn't isolate satellites, try building one 36° sector explicitly:

1. Identify the tile shapes in one sector from the reference
2. Use `connect cycle` or `face` statements to define each tile
3. Use `rotate 10` to replicate around the center

## Secondary Changes (only if structural improves)
- Increase turquoise in outer ring: `fill void where ring >= 2 and sides == 3 color turquoise`
- Add scalloped boundary (future iteration)
