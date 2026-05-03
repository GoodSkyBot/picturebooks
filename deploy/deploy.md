# Dokku Deployment

## Deployment Model

This repository can be deployed as a static site behind nginx in Dokku.

The container copies the repository into `/app` and serves it directly.

## URL Layout

- `/` serves the root `index.html`
- `/books/{slug}/` serves a generated book directly

If you want cleaner URLs such as `/frogs`, add rewrite rules that map `/{slug}` to `/books/{slug}/`, or add a publish step that mirrors generated book folders to the repo root.

## Build Files

- `deploy/Dockerfile`
- `deploy/nginx.conf`

## Dokku Setup

Create the app:

```bash
dokku apps:create picturebooks
```

Tell Dokku to use the Dockerfile in `deploy/`:

```bash
dokku builder-dockerfile:set picturebooks dockerfile-path deploy/Dockerfile
```

Add a git remote:

```bash
git remote add dokku dokku@your-server:picturebooks
```

Deploy:

```bash
git push dokku master
```

## Notes

- Each generated book should live at `books/{slug}/` and include its own `index.html`.
- If you want `/{slug}` URLs instead of `/books/{slug}/`, add explicit nginx rewrite rules or generate per-slug folders at the repo root during publish time.
