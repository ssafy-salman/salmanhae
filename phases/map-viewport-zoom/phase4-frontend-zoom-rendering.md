# Phase 4: Frontend Zoom Rendering

## Goal
Render different marker styles for region averages, clusters, and individual properties so the map stays readable at every zoom level.

## Files
- `frontend/src/components/map/*` - Add marker rendering for `REGION_AVG`, `CLUSTER`, and `PROPERTY`
- `frontend/src/stores/*` - Maintain counts and selected item behavior per viewport mode
- `frontend/src/utils/*` - Add formatting helpers if existing helpers are insufficient

## Done When
- [ ] broad zoom levels show region average markers instead of thousands of property labels.
- [ ] cluster mode shows compact cluster markers with count and representative price.
- [ ] detailed zoom shows individual property markers.
- [ ] side list behavior remains useful and does not try to render region-average items as property cards.

## Architecture Rules
- UI follows `docs/04_UI_GUIDE.md`: region averages and clusters should reduce clutter and keep the map dominant.
- Text must not overflow markers or controls on desktop/mobile viewports.
- Components should remain focused and avoid card nesting or unrelated visual changes.

## Implementation Instructions
Use the backend `mode` and item `type` fields to decide rendering. Keep marker labels short and stable; long names should be omitted or truncated in markers and shown in side panels if needed.
