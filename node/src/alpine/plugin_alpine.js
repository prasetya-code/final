// Import core Alpine.js
import Alpine from 'alpinejs'

// Import plugin masking input (format nomor telepon, tanggal, dll)
import mask from '@alpinejs/mask'

// Import plugin persist (simpan state ke localStorage otomatis)
import persist from '@alpinejs/persist'

// Import plugin intersect (deteksi elemen masuk/keluar viewport)
import intersect from '@alpinejs/intersect'

// Import plugin collapse (animasi buka/tutup elemen)
import collapse from '@alpinejs/collapse'

// Import plugin focus (manajemen focus keyboard/aksesibilitas)
import focus from '@alpinejs/focus'

// Daftarkan semua plugin ke Alpine
// Harus dilakukan SEBELUM Alpine.start()
Alpine.plugin(mask)
Alpine.plugin(persist)
Alpine.plugin(intersect)
Alpine.plugin(collapse)
Alpine.plugin(focus)

// Expose Alpine ke window agar bisa diakses dari template HTML
// Contoh: <div x-data="{ ... }"> bisa baca window.Alpine
window.Alpine = Alpine