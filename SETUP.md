# Setup — 5 minutes

## 1. Create the magic repo
Create a new **public** repository named exactly `Prithvi8706` (same as your username).
GitHub will show the "special repository" banner — that's the confirmation.

## 2. Push these files

```powershell
cd path\to\this\folder
git init
git add .
git commit -m "liquid glass profile — silver"
git branch -M main
git remote add origin https://github.com/Prithvi8706/Prithvi8706.git
git push -u origin main
```

## 3. Fill in the three placeholders in README.md
- `https://YOUR-PORTFOLIO-URL.vercel.app` → your Mythos deployment URL
- `YOUR-LINKEDIN` → your LinkedIn slug
- `YOUR-EMAIL` → your contact email

## 4. Activate the snake
Go to the repo → **Actions** tab → enable workflows → select **generate-snake** → **Run workflow**.
It writes the silver snake SVG to an `output` branch; the README already points at it.
(Until the first run completes, that one image will 404 — everything else works immediately.)

## 5. Verify animations
Open your profile in a normal browser tab (not the mobile app's markdown preview).
You should see: drifting mist, the light sweep across the glass, typing status line,
the pulsing silver mist, and the slow scanline.

## Tuning knobs
- **Animation speed:** every `@keyframes` duration lives in the `<style>` block at the top of each SVG.
- **Mist density:** `stop-opacity` values in the `mist` / `mistSilver` gradients.
- **Glow intensity:** `stdDeviation` in the `silverGlow` filter.
- **Text:** all copy is plain `<text>` elements in `assets/hero.svg` — edit freely.

## Constraint reminders (so future edits don't silently break)
- No JavaScript, no `:hover`, no external fonts/images inside the SVGs — GitHub renders them as `<img>`, so only self-contained CSS/SMIL animation survives.
- Relative image paths (`assets/hero.svg`) work on the profile page; keep the folder name.
- GitHub caches images through its camo proxy — after editing an SVG, a hard refresh (Ctrl+F5) may be needed to see changes.
