import { defineConfig } from 'vite'
import legacy from '@vitejs/plugin-legacy'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    legacy({ targets: ['defaults', 'not IE 11'] }),
    tailwindcss()
  ],

  build: {
    outDir: '../app/static/dist',
    emptyOutDir: true,
    reportCompressedSize: false,

    rollupOptions: {
      input: {
        main: path.resolve(__dirname, './src/main.js'),
      },

      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',

        assetFileNames: ({ name }) => {
          if (name && name.endsWith('.css')) {
            return 'tailwindcss.css';
          }
          return 'assets/[name].[ext]';
        },
      },
    },
  },
})