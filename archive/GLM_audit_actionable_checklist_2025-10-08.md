# Lumen Frontend UI Actionable Checklist
**Scope**: Auth Modal • Router • Profile • Gallery Modules  
**Single Source**: Align active work with `docs/GLM_audit_2025-10-07_20-34.md`; move overflow items into the queue below.

## Active Work (≤6 items)
- [ ] **Add Welcome Toast to Auth Success** — `frontend/js/modules/auth.js:127`; ~30 m. Replace the TODO by calling `LumenUtils.showSuccess(\`Welcome back, ${user.display_name}!\`)` once `onSignIn()` resolves.
- [ ] **Replace Blocking Sign-out Confirm** — `frontend/js/modules/profile.js:517`; ~1.5 h. Implement a non-blocking confirmation modal via `ui.js`, including ESC/Enter handling and consistent styling.
- [ ] **Fix Series Dropdown in Photo Edit** — `frontend/js/modules/gallery.js:1025`; ~1 h. Complete `loadSeriesOptions()` with error handling, dropdown population, and a “Create new series” affordance.
- [ ] **Add Auth Modal Loading States** — `frontend/js/modules/auth.js`, `frontend/js/templates.js`; ~2 h. Add spinner/disable logic during Google sign-in, surface retry-friendly errors, and restore controls on failure.
- [ ] **Implement Router Loading Skeletons** — `frontend/js/modules/router.js`, `frontend/js/templates.js`; ~2 h. Show skeleton components during `loadRoute()` transitions and add lightweight fade transitions.
- [ ] **Standardize Modal System** — `frontend/js/modules/ui.js`, `frontend/js/templates.js`; ~2 h. Introduce a shared `showConfirm()` API, unify backdrop click behavior, and add a focus trap for accessibility.

## Queue (pull into Active when capacity frees up)
- **Navigation State Management Enhancements** (audit Task 6) — Improve breadcrumbs, active state highlighting, and history handling within `router.js`/`app.js`.
- **Micro-interactions & Animations** (audit Task 7) — Extend animation patterns for modals, buttons, and loading spinners across `frontend/css/components.css` and `frontend/js/modules/ui.js`.
- **Accessibility Improvements** (audit Task 8) — Add ARIA labels, focus trapping, skip links, and screen-reader announcements in `ui.js` and `router.js`.
- **Enhance Profile Settings Navigation** — Improve tab indicators, keyboard navigation, and mobile responsiveness in `frontend/js/modules/profile.js` (≈1 h).
- **Add Gallery Error States** — Introduce retry flows, empty-state messaging, and offline detection in `frontend/js/modules/gallery.js` (≈1 h).
- **Improve Mobile Auth Experience** — Increase touch targets, refine mobile animations, and address iOS viewport quirks in auth modules (≈1.5 h).
- **Add Keyboard Navigation Helpers** — Provide global skip links, modal tab order enforcement, and ARIA labeling in `frontend/js/modules/router.js` and `frontend/js/modules/ui.js` (≈1 h).
- **Fix Auth Modal Close Button** — Ensure an accessible close control in `frontend/js/templates.js` and `frontend/index.html` (≈30 m).
- **Add Route Change Feedback for Dev** — Add structured logging hooks for `router.js` to help trace navigation during development (≈30 m).
- **Improve Auth/Gallery Error Messaging** — Deliver actionable error copy in `frontend/js/modules/auth.js` and `frontend/js/modules/gallery.js` (≈45 m).
- **Add Gallery Loading Indicators** — Surface spinners/placeholders during async photo operations in `frontend/js/modules/gallery.js` (≈30 m).

## ✅ Success Metrics
- [ ] All three original TODOs resolved (`auth.js`, `profile.js`, `gallery.js`).
- [ ] Non-blocking modal patterns across sign-out and confirmation flows.
- [ ] Loading states implemented for auth and router transitions.
- [ ] Mobile auth flow and keyboard navigation validated.
- [ ] Consistent modal API with focus management and retry-friendly error UX.

## Reference
- Detailed rationale and sequencing: `docs/GLM_audit_2025-10-07_20-34.md`
