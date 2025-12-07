# Decision Log

This document consolidates architecture and implementation decisions that were previously scattered across multiple files.

## Lightbox Implementation Comparison

**Decision:** Use **PhotoSwipe** for single-image lightboxes.

**Reasoning:** PhotoSwipe's dynamic-loading "Lightbox" wrapper is ideal for a mobile-first PWA. It minimizes the initial JavaScript payload by only loading the core library when a user interacts with an image. This improves initial page load speed and provides a high-quality, smooth experience on touch devices.

### Alternatives Considered:

*   **GLightbox:** Simple, pure JS solution, good for mixed media types.
*   **lightGallery:** Very feature-rich, but requires more plugins and has a larger initial payload.
*   **baguetteBox.js:** The smallest and most minimal option, but lacks features.

---

## Original React/TypeScript Implementation Guide

This section contains the original specification for a React-based frontend. While the project has since evolved, this information is preserved for historical context.

**Stack (as of Sep 2025 spec):** React 19.1.1 + TypeScript 5.8.3 + Radix UI Themes + Vite 7.1.2

### Core Dependencies from Spec:
```json
{
  "react": "^19.1.1",
  "react-dom": "^19.1.1",
  "@radix-ui/themes": "^3.2.1",
  "@radix-ui/react-icons": "^1.3.2",
  "react-router-dom": "^7.8.2",
  "react-responsive-masonry": "^2.7.1",
  "yet-another-react-lightbox": "^3.25.0"
}
```

### Proposed Additional Dependencies:
- `axios` (API calls)
- `@tanstack/react-query` (Data fetching)
- `zustand` (State management)
- `react-hook-form` (Forms)
- `zod` (Schema validation)
- `date-fns` (Date formatting)
- `react-intersection-observer` (Infinite scroll)

### Key Architectural Points from Spec:
*   **State Management:** `Zustand` for simple, global state.
*   **Data Fetching:** `React Query` for server state, caching, and synchronization.
*   **API Layer:** An `axios` client with interceptors for auth tokens and error handling.
*   **Styling:** A "Glassmorphism" theme built on top of `Radix UI Themes`.
*   **Components:** A detailed breakdown of components like `AppShell`, `PhotoCard`, `SeriesCard`, and pages for `Discovery`, `Profile`, etc.
*   **Types:** Comprehensive TypeScript type definitions for all major data models (User, Photo, Series, etc.).

(For the full, detailed specification, refer to the original document in the `backup/docs` directory).
