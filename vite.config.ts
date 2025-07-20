import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/holoca_list_repo/',
  plugins: [vue()],
})