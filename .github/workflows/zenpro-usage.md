ZenPro Secret Integration

This repository has the `zenpro` repository secret configured and ready to use in GitHub Actions workflows.

## Direct Usage (Recommended)

Access the secret directly in your workflows:

```yaml
env:
  ZENPRO: ${{ secrets.zenpro }}

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - name: Use zenpro secret
        run: echo "Using ZENPRO (masked by GitHub)"
```

Or pass it directly to a step:

```yaml
jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - name: Make API call
        run: curl https://api.zencreator.pro/api/... -H "Authorization: Bearer ${{ secrets.zenpro }}"
```

## Reference Test

See `.github/workflows/zenpro-direct-test.yml` for a working example that verifies the secret is accessible during workflow runs.