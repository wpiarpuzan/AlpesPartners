Postgres image build & publish
=================================

This workflow builds the `alpespartners-postgres` image from `docker/postgres/Dockerfile` and pushes it to a container registry (GHCR by default).

Required repository secrets (GitHub):

- `REGISTRY_HOST` (optional) - registry hostname, defaults to `ghcr.io`.
- `REGISTRY_USERNAME` - the username or org in the registry (GHCR username/org).
- `REGISTRY_TOKEN` - a personal access token with package write/push permissions.

How to trigger

1. Push to branch `feature/postgres-image` (the workflow runs on push).
2. Or trigger manually from the Actions tab using `workflow_dispatch`.

How to consume the published image

Set the `USE_LOCAL_POSTGRES_IMAGE` environment variable for local runs or CI to the published image name:

```powershell
$env:USE_LOCAL_POSTGRES_IMAGE = 'ghcr.io/<user-or-org>/alpespartners-postgres:latest'
docker-compose up -d --remove-orphans
```

Notes

- The workflow uses `docker/build-push-action` and `docker/login-action`. Provide a token that has permission to push packages to your registry.
- For GHCR set `REGISTRY_HOST=ghcr.io`, `REGISTRY_USERNAME=<your-gh-username-or-org>`, and `REGISTRY_TOKEN` to a PAT with `write:packages` scope.
