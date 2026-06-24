# Phase 5: QA Docs Deploy

## Goal
Verify the zoom-aware map flow end to end, update documentation if the implemented API differs, and deploy through the existing CI/CD path.

## Files
- `docs/08_API_SPEC.md` - Update only if the implemented response differs from the current contract
- `docs/07_DOMAIN_MODEL.md` - Update only if a schema/model change was introduced
- `docs/04_UI_GUIDE.md` - Update only if UI behavior policy changed
- `.github/workflows/*` - No change expected; existing backend/frontend deployment paths should be used

## Done When
- [ ] backend tests pass.
- [ ] frontend tests/build pass.
- [ ] deployed map no longer attempts to render thousands of markers at broad zoom.
- [ ] Cloud Run and Vercel deployments use the existing CI/CD flow without secret changes.

## Architecture Rules
- API/domain documentation must stay synchronized with implemented response or schema changes.
- Deployment uses Cloud Run for Spring Boot and Vercel for frontend; FastAPI is not part of this F-1 map rendering change.

## Implementation Instructions
Capture before/after behavior on deployed or local production build. If only backend and frontend code changed, rely on the existing GitHub Actions and Vercel integration after merge to `develop`.
