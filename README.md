# Whning's personal site

This is a small static GitHub Pages site for study notes, software, and work in progress.

The homepage is plain HTML and CSS. It has no build step and no runtime dependency.

## Local preview

```text
python -m http.server 8000
```

Open `http://127.0.0.1:8000/` in a browser.

## Deployment

Pushing to `main` runs `.github/workflows/pages.yml`, which publishes the repository root through GitHub Pages.
