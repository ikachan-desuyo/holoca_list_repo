# GitHub Pages で Vite + Vue プロジェクトを公開する手順

## 1. `vite.config.ts` の `base` 設定

リポジトリ名が `holoca_list_repo` の場合、下記のように設定します。

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

## 2. `index.html` をプロジェクト直下に配置

- `index.html` は必ずプロジェクトのルートディレクトリに置く。

---

## 3. 静的ファイル（例: features.json）は `public/` に置く

- 例: `public/features.json` → ビルド後は `dist/features.json` になる。

---

## 4. ビルド

```sh
npm run build
```

---

## 5. `gh-pages` ブランチを作成し、`dist/` の中身を配置

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

## 6. GitHub のリポジトリ設定

- 「Settings」→「Pages」
- 「Branch」を `gh-pages`、「/ (root)」を選択

---

## 7. 公開URL

```
https://<GitHubユーザー名>.github.io/holoca_list_repo/
```

---

## 8. 注意点

- `base` 設定を忘れない
- `index.html` はルートに
- 静的ファイルは `public/` に
- `gh-pages` ブランチには `dist/` の中身だけ