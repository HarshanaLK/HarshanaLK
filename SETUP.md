# GitHub Profile Setup — Harshana Karunarathna

This project is adapted from the uploaded `Shahzaib-Malik77-main` terminal-style GitHub profile example. The complete code and personal details are customized for **Harshana Karunarathna / @HarshanaLK**.

## What's in the project?

| File | Purpose |
|---|---|
| `README.md` | GitHub profile main content, hero and projects panels |
| `dark.svg` | Code-only vector portrait + profile banner for dark mode |
| `light.svg` | Code-only vector portrait + profile banner for light mode |
| `projects.svg`, `projects-light.svg` | Code-generated project cards |
| `profile.json` | Editable name, education, skills, links and contact information |
| `projects.json` | Projects shown in GitHub profile |
| `generate_profile.py` | Generates SVG vector shapes from your photo without embedding raster image data |
| `.github/scripts/fetch_data.py` | Fetches repository stars, language usage and last activity |
| `.github/scripts/generate_projects.py` | Draws project cards as pure vector SVGs |
| `.github/workflows/projects.yml` | Refreshes SVG project cards every 6 hours or on demand |
| `.github/workflows/snake.yml` | Generates contribution snake code as SVG on demand |
| `requirements.txt` | Python image-processing dependency, only needed to *regenerate* your vector portrait |

The ZIP deliberately does **not** include any `.png`, `.jpg`, `.jpeg`, or `.webp` images. `dark.svg` and `light.svg` already contain the vector path data for the uploaded portrait and will work immediately when uploaded to GitHub.

> Note: A vector mosaic can retain much more detail than ASCII art, but it is an approximation of a photograph, not pixel-for-pixel photo-identical. It uses SVG `<path>` drawing commands only. There is no `<image>` element, data-URI raster, or base64 embedded photo.

## Quick setup: Upload with the GitHub web interface

1. Open the existing profile repository: **https://github.com/HarshanaLK/HarshanaLK**.
2. Back up your current `README.md` if you want to retain it.
3. Extract the ZIP. Upload **all** the files and the `.github` folder from `harshana-profile-custom` to the **root of your profile repository**. **Keep the `.github` directory structure.**
4. Replace the existing `README.md` when GitHub asks, or edit the existing file and paste the supplied README contents. If you use Git commands, this replacement is straightforward.
5. Commit changes to `main`.
6. Open **https://github.com/HarshanaLK** and verify the dark/light banner and project cards.

You don't need to install Python to display the supplied code-generated SVGs.

## Upload with Git (Windows PowerShell)

```powershell
# Clone your existing GitHub profile repository
# Skip this if you've already cloned it.
git clone https://github.com/HarshanaLK/HarshanaLK.git
cd HarshanaLK

# Copy the extracted project's contents into this folder,
# including the hidden .github directory.

git add README.md profile.json projects.json dark.svg light.svg projects.svg projects-light.svg generate_profile.py requirements.txt SETUP.md .github

git commit -m "Redesign profile with custom vector portrait and terminal panels"
git push origin main
```

## Customize your info

- Edit `profile.json` to change your name, technical skills, university, profile description, links and email.
- Edit `projects.json` to control which repositories appear in the projects card grid. Use `HarshanaLK/repo-name` for each repository.
- To apply changes from `profile.json` to `dark.svg` and `light.svg`, rerun the portrait generator (see below).
- To apply changes from `projects.json`, GitHub Actions automatically regenerates `projects.svg` and `projects-light.svg` after a push. You can also generate locally.

## Regenerate the portrait from your own photo (optional)

The current `dark.svg` and `light.svg` already contain the customized portrait. Only follow these steps if you want to make changes or use a different original photo.

```powershell
py -m pip install -r requirements.txt
py generate_profile.py --photo "C:\path\to\your\portrait.png"
```

If `py` is not available, use `python -m pip install -r requirements.txt` and `python generate_profile.py ...`.

The script generates **real SVG vector paths**, not an SVG wrapper around a photo. For a more detailed mosaic:

```powershell
py generate_profile.py --photo "C:\path\to\your\portrait.png" --tiles 180 --colors 128
```

The `--tiles` option changes the resolution, and `--colors` changes palette size. More tiles can increase SVG file size.

## Project cards: refresh and updates

The included project card SVGs work immediately after upload, but initially show `0` stars and `n/a` activity until live repository data is refreshed.

1. In GitHub, open your `HarshanaLK/HarshanaLK` repository → **Actions**.
2. If Actions are disabled, enable them for this repository.
3. Under **Settings → Actions → General → Workflow permissions**, choose **Read and write permissions** if your repository permits it.
4. Select **Update code-only SVG project cards** → **Run workflow**.
5. The workflow fetches live GitHub project data and commits updated `projects.svg` and `projects-light.svg` to `main`. It also runs every 6 hours and after edits to `projects.json`.

If your main branch has protection rules preventing bot pushes, manually run the scripts and commit outputs, or adjust the workflow to open a PR instead.

Local generation without live repo data:

```powershell
py .github/scripts/generate_projects.py projects.json .
```

## Contribution snake animation (optional)

The source project includes a contribution snake. This project also provides it **as SVG-only code output**.

1. Open **Actions** → **Update contribution snake SVG** → **Run workflow**.
2. GitHub Actions creates or updates the `output` branch with `snake-light.svg` and `snake-dark.svg`.
3. Open `README.md` and uncomment the `CONTRIBUTION SNAKE` picture block.

The snake image link intentionally starts commented out so it won't be broken before the first action run.

## GitHub README limitations

GitHub sanitizes inline `<svg>` markup inside README files, so the README uses an `<img>` element within a `<picture>` tag to **display code-generated SVG files**. That `<img>` reference does **not** mean there is an embedded PNG/JPG photo; the SVG files are text files containing drawing commands. Static HTML/CSS and ASCII alone cannot reproduce a face with exact photographic fidelity.

GitHub theme switching uses `prefers-color-scheme`, and SVG SMIL animation support can vary by viewer.

## Troubleshooting

- **Banner isn't visible:** Verify `dark.svg` and `light.svg` are in the repo root and committed on `main`.
- **Still showing old profile:** Hard-refresh the browser; GitHub's raw content CDN can cache images briefly.
- **Project cards don't update:** Check GitHub Actions workflow permissions and workflow logs.
- **Snake missing:** Run the snake workflow once, then uncomment the README block.
- **SVG too big:** Regenerate the vector portrait with fewer tiles (`--tiles 128`) or fewer colors (`--colors 64`).
