# Spec: Modern Web Guidance Frontend Optimizations

## 1. Objective
Implement the 3 Modern Web Guidance quick wins across the Docusaurus frontend architecture:
1. **Font Preconnecting & Render-Blocking Optimization**: Migrate Google Fonts from blocking CSS `@import` to asynchronous preconnected `<link>` tags in `docusaurus.config.js` `headTags`.
2. **Native Color-Scheme & Browser UI Theming**: Declare explicit `color-scheme: light;` and `color-scheme: dark;` in `custom.css` to properly theme browser scrollbars, form controls, and prevent theme flashes.
3. **Advanced Typographic Wrapping (`text-wrap: pretty` & `text-wrap: balance`)**: Apply `text-wrap: pretty` to `.markdown p` and `text-wrap: balance` to headings to prevent orphaned words ("runts") across all 41 module theory pages.

---

## 2. Tech Stack & Environment
- **Framework:** Docusaurus v3.9.2 (React 18, Webpack 5)
- **Target Files:**
  - `doc/docusaurus.config.js`
  - `doc/src/css/custom.css`
- **Verification Commands:**
  - `npm run build` (in `doc/`)
  - HTML inspection in `doc/build/`

---

## 3. Implementation Details

### A. `doc/docusaurus.config.js` (`headTags`)
Add preconnect hints and non-blocking font stylesheets:
```javascript
headTags: [
  {
    tagName: 'link',
    attributes: {
      rel: 'preconnect',
      href: 'https://fonts.googleapis.com',
    },
  },
  {
    tagName: 'link',
    attributes: {
      rel: 'preconnect',
      href: 'https://fonts.gstatic.com',
      crossorigin: 'anonymous',
    },
  },
  {
    tagName: 'link',
    attributes: {
      rel: 'stylesheet',
      href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap',
    },
  },
],
```

### B. `doc/src/css/custom.css`
1. Remove `@import url('https://fonts.googleapis.com/css2?...');`
2. Add `color-scheme: light;` under `:root`
3. Add `color-scheme: dark;` under `[data-theme='dark']`
4. Add:
```css
.markdown h1,
.markdown h2,
.markdown h3,
.markdown h4 {
  text-wrap: balance;
}

.markdown p {
  text-wrap: pretty;
}
```

---

## 4. Verification & Testing Strategy
1. Build verification: `npm run build` inside `doc/`.
2. Inspect `doc/build/index.html` to confirm `rel="preconnect"` tags are present in `<head>`.
3. Confirm zero broken links or CSS syntax errors.

---

## 5. Success Criteria
- Docusaurus build succeeds with 0 errors.
- Render-blocking CSS import eliminated.
- Text typography and browser scrollbar theme natively synchronized.
