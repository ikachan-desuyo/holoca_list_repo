# holoca_list_repo

This project is a Vite + Vue web application for Hololive card recognition using camera input and feature matching.

---

## 🚀 How to Deploy to GitHub Pages

### 1. Set the `base` in `vite.config.ts`

Set the `base` option to your repository name:

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/holoca_list_repo/',
  plugins: [vue()],
})
```

---

### 2. Place `index.html` at the Project Root

- Make sure `index.html` is in the root directory of your project.

---

### 3. Put Static Files (e.g., `features.json`) in `public/`

- Example: `public/features.json` will be available as `/features.json` after build.

---

### 4. Build the Project

```sh
npm run build
```

---

### 5. Deploy the `dist/` Contents to the `gh-pages` Branch

```sh
git checkout --orphan gh-pages
git rm -rf .
cp -r dist/* .
git add .
git commit -m "Deploy to GitHub Pages"
git push -u origin gh-pages
git checkout main
```

---

### 6. GitHub Repository Settings

- Go to **Settings** → **Pages**
- Set the source branch to `gh-pages` and the folder to `/ (root)`

---

### 7. Access Your Published Site

```
https://<your-github-username>.github.io/holoca_list_repo/
```

---

### 8. Notes

- Do not forget to set the correct `base` in `vite.config.ts`
- `index.html` must be at the project root
- Place static files (like `features.json`) in the `public/` directory
- Only the contents of `dist/` should be in the `gh-pages` branch

---

## 📷 Features

- Camera-based Hololive card detection
- Feature extraction and matching using `features.json`
- Works fully in the browser (no server-side required)

---

## 🛠️ Development

```sh
npm install
npm run dev
```

---

## 📝 License