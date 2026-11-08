# Fix the missing GitHub contribution snake animation

## Verified issue

At the time of inspection, `HarshanaLK/HarshanaLK` did not have an `output` branch. That means `snake-light.svg` and `snake-dark.svg` were not published at the links used by your README.

## Apply this fix

1. Open https://github.com/HarshanaLK/HarshanaLK/blob/main/.github/workflows/snake.yml
2. Click Edit (pencil) and replace the content with the `snake.yml` supplied in this ZIP.
3. Commit to `main`. This workflow is configured to trigger on its own updated file, and can also run manually.
4. Open https://github.com/HarshanaLK/HarshanaLK/actions/workflows/snake.yml, select **Run workflow**, choose `main` and start the run.
5. Check that all three steps are green: Generate light and dark animated snakes; Verify both SVG files were generated; Publish generated SVGs to the output branch.
6. Check https://github.com/HarshanaLK/HarshanaLK/tree/output and confirm `snake-dark.svg` and `snake-light.svg` exist.
7. Visit https://github.com/HarshanaLK to see the animated contribution snake. Hard-refresh if GitHub caches an old image.

## If the publishing step fails

- Open Settings → Actions → General → Workflow permissions and enable **Read and write permissions** (if the setting is available).
- Make sure repository/org rules allow GitHub Actions to create the `output` branch.
- Read the failed step log to see the precise error. The output branch will not exist until publishing succeeds.

## Note

SVG animated snakes are generated from your *contribution history*. They are different from your `dark.svg`/`light.svg` portrait. The portrait is primarily a static drawing with a subtle animated indicator.
