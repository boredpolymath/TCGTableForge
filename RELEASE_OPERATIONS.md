# Release operations

## Deployment

The `Build and deploy Pages` workflow runs checks for pull requests. A push to `main` or a manual workflow run builds the selected revision, runs its checks, and deploys the artifact to GitHub Pages after the build succeeds.

## Rollback

Before the first release, record the successfully deployed commit as the initial known-good revision. For a later rollback, open **Actions → Build and deploy Pages → Run workflow** and select that commit or its release tag. The workflow builds and deploys the selected revision. Confirm the deployment URL and service-worker version after the run.

Keep the last known-good commit or release tag available until a replacement deployment passes its smoke checks.
