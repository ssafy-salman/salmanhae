# Phase 4: Frontend Zoom Rendering

## Goal
Render different marker styles for region averages, clusters, and individual properties so the map stays readable at every zoom level.

## Files
- `frontend/src/views/MapExplorer.vue` - Render `REGION_AVG`, `CLUSTER`, and `PROPERTY` markers by viewport item type
- `frontend/src/store/mapStore.js` - Keep side-list properties derived from property viewport items only
- `frontend/src/utils/mapViewport.js` - Add viewport item classification, label, and marker anchor helpers
- `frontend/src/utils/mapViewport.test.mjs` - Verify marker type, label, price, anchor, and property-only list behavior
- `frontend/package.json` - Run all frontend `.test.mjs` files

## Done When
- [x] broad zoom levels show region average markers instead of thousands of property labels.
- [x] cluster mode shows compact cluster markers with count and representative price.
- [x] detailed zoom shows individual property markers.
- [x] side list behavior remains useful and does not try to render region-average items as property cards.

## Architecture Rules
- UI follows `docs/04_UI_GUIDE.md`: region averages and clusters should reduce clutter and keep the map dominant.
- Text must not overflow markers or controls on desktop/mobile viewports.
- Components should remain focused and avoid card nesting or unrelated visual changes.

## Implementation Instructions
Use the backend `mode` and item `type` fields to decide rendering. Keep marker labels short and stable; long names should be omitted or truncated in markers and shown in side panels if needed.
