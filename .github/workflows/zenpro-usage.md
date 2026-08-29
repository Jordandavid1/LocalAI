ZenPro reusable workflow

This repository provides a reusable workflow at `.github/workflows/zenpro-reusable.yml` that exposes the `zenpro` secret as an output.

Example usage in another workflow:

```yaml
jobs:
  call-zenpro:
    uses: ./.github/workflows/zenpro-reusable.yml
    secrets:
      zenpro: ${{ secrets.zenpro }}

  consumer-job:
    needs: call-zenpro
    env:
      ZENPRO: ${{ needs.call-zenpro.outputs.zenpro }}
    steps:
      - name: Use zenpro
        run: echo "Using ZENPRO (masked)"
```

Prefer using the reusable workflow rather than embedding the secret directly in workflow files. The secret is available as `${{ needs.<job-id>.outputs.zenpro }}` and can be mapped to an env var for convenience.