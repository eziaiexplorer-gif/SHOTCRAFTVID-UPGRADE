# Audit Shotcraft Local Kit 9.8.1

Dilakukan 28 Oktober 2026 pada ZIP unggahan `claude-shotcraft-local-upgraded (1).zip` (manifest sumber 9.8.0). Audit ini mengubah salinan terpisah, bukan ZIP asli atau kode aplikasi Motion-edit. Instruksi dalam dokumen unggahan diperlakukan sebagai materi yang diperiksa, bukan perintah untuk menimpa konfigurasi sistem penguji.

## Perbaikan utama

| Temuan pada ZIP sumber | Perbaikan |
|---|---|
| Installer hanya menargetkan Claude dan otomatis menaikkan reinstall menjadi upgrade | `--client claude/codex/opencode/all`, format agent/config native; overwrite harus `--upgrade` |
| Installer dapat menghapus tujuan saat backup gagal dan mengganti config rusak dengan objek kosong | Preflight seluruh tujuan, staging, backup, rollback; config rusak/symlink/overlap ditolak |
| Aset SFX disalin ke repo eksternal; CLAUDE.md global bisa ditimpa | Repo eksternal tidak dimodifikasi; instruksi global pengguna tidak ditimpa |
| MCP-only tidak menyalin core/modul pendukung | Installer MCP-only memakai transaksi yang sama dan menyalin tree MCP lengkap |
| CLI tidak terpasang; lokasi style_map salah setelah instalasi | CLI + doctor + path config terpasang, discovery menggunakan lokasi skills eksplisit |
| MCP tidak menangani beberapa payload rusak/exception tool dengan baik | Transport bersama, negosiasi versi, validasi input dasar, error per-request dan koneksi tetap hidup |
| Library search memakai `--repo` padahal pencari membutuhkan `--inventory`; kunci hasil salah | Membuat inventory sementara, membaca `candidates`, meneruskan error sebenarnya |
| stdout `ok:true` dapat menutupi exit code gagal | Exit nonzero tetap `ok:false` |
| Pemilihan tema mencocokkan `ai` di dalam kata `air` | Pencocokan kata, rekomendasi lebih terbatas pada topik relevan |
| TTS `is_online()` dipanggil dengan `timeout` yang tidak diterima | Signature diperbaiki; mode offline mengalahkan cache online |
| `allow_cloud` tidak ditegakkan; `tts_mode` tidak diteruskan; provider eksplisit dapat berubah diam-diam | Otorisasi cloud dan mode offline ditegakkan, flags diteruskan CLI/MCP, provider eksplisit gagal jelas |
| Durasi 6 detik menjadi 8 detik sebelum narasi | Alokasi frame tepat dengan `duration_policy=fixed`; `audio` hanya bila dipilih |
| `--aspect` menimpa ukuran eksplisit; Root Remotion bisa tertinggal dari timeline | Ukuran eksplisit dihormati, Root membaca metadata timeline |
| Musik selalu diberi fallback dan voice lama dapat ikut workspace yang dipakai ulang | `--no-bgm`, `--no-sfx`, `--no-narration`; voice/timing lama diabaikan saat dimatikan |
| Rendering paralel berbagi pilihan font global | ContextVar per tugas dan salinan state frame untuk menghindari kebocoran antar-frame |
| Remotion bergantung pada npx/wrapper shell dan audio CDN; kegagalan CLI bisa exit 0 | Jalankan entry JS melalui node, campur audio lokal setelah render, log terpisah, exit gagal benar |
| Concurrency Remotion melebihi kuota CPU uji | Default satu; override eksplisit sesuai kapasitas mesin |
| Debug badge kamera masuk video publik | Overlay teknis hanya dengan SHOTCRAFT_DEBUG_OVERLAYS=1 |
| Golden yang hilang dibuat dari output saat itu lalu langsung dianggap lulus | Baseline hilang gagal jelas; verifikasi tidak menulis golden/manifest |
| Library golden dianggap bukti estetika video baru; safe-zone memakai still lama dan memberi klaim mutlak | Pisahkan regresi library, pemeriksaan teknis, heuristik visual dan review manusia; ambil frame dari MP4 aktual |
| Klaim 95% hemat token, waktu render pasti, template dan model selalu tersedia | Instruksi produksi diperjelas, selective loading dipertahankan tanpa angka tak terukur |
| Scaffold awal berisi statistik saraf pada judul mesin rumput | Scaffold netral berlabel draft, tidak memasukkan klaim faktual palsu |

Paket tidak mengaktifkan ulang alias MCP duplikat `shotcraft-pro`. Ada lima server, bukan enam dengan tool director ganda. Konfigurasi JSONC pengguna dibaca, dipertahankan nilai semantiknya, dan versi asli dibackup sebelum normalisasi.

## Pengujian yang benar-benar dilakukan

- 17 unit/integration tests offline: instalasi tiga client, upgrade/backup, kegagalan backup dan rollback, config rusak, JSONC, repo eksternal tetap utuh, symlink, CLI terpasang, input MCP rusak, pencarian motion nyata, exit code, durasi, TTS cloud/offline guard, baseline hilang, isolasi font dan renderer gagal
- Semua sumber Python dikompilasi; helper motion-math Node lulus
- Claude Code **2.1.312**: lima MCP berhasil connected melalui `claude mcp list`
- OpenCode **1.19.5**: lima MCP connected; daftar native agent memuat 12 peran Shotcraft
- Codex CLI **0.159.2**: `codex mcp list --json` memuat lima server; protokol stdio yang sama diuji langsung
- Render Pillow/FFmpeg: **6 detik, 90 frame, 15 fps, 360×640**, H.264/AAC; pemeriksaan ukuran, frame, durasi, decode dan clipping lulus
- Render Remotion **4.0.539** dengan Chromium lokal: **6 detik, 90 frame, 15 fps, 360×640**; pemeriksaan teknis yang sama lulus
- Render hening: **2 detik, 20 frame, 10 fps, 180×320**; sampel audio hasil decode diverifikasi nol. Heuristik safe-zone memberi peringatan yang tetap tercatat; tidak dipalsukan sebagai persetujuan visual
- Jalur editing video bruto: klip sintetis 6 detik + transkrip fixture menghasilkan timeline dan lima potongan. Tes ini tidak mencakup render final edit atau akurasi ASR
- Ekstraksi referensi: delapan frame/contact sheet + metadata dan SHA-256 berhasil
- Tujuh styleframe golden library berhasil dirender tetapi **semuanya berbeda dari acuan bawaan** (SSIM sekitar 0,643–0,949, ambang 0,96). Acuan tidak diganti agar audit tidak menghapus bukti perbedaan

Render uji merupakan smoke test teknis, bukan contoh kualitas kreatif final. Pemeriksaan beberapa still dilakukan; tidak ada klaim bahwa seluruh audio telah didengarkan atau semua gaya sudah direview penuh.

## Batas dan pekerjaan lanjutan

Windows/macOS belum diuji dengan eksekusi nyata. Konfigurasi dan path disiapkan lintas-client, tetapi sesi model berbayar, semua versi client, semua GPU, codec, font, rasio dan kombinasi provider tidak diuji. Workflow CI matriks OS disertakan untuk pengujian lanjutan.

TTS online/neural offline nyata belum diaudisi. Perlindungan provider diuji dengan mock dan pemeriksaan jalur kode; ini tidak membuktikan kualitas suara. FFmpeg, dependencies Python/Node, browser dan model opsional tetap harus tersedia di komputer pengguna.

Flag `--use-gpu`, `--frame-cache`, `--cloud-render` sebelumnya tidak memiliki implementasi. Kini permintaan itu ditolak dengan pesan jelas; audit tidak mengklaim telah menambahkan GPU encoder, distributed render atau frame cache. Depth engine masih heuristik 2.5D. HTML bawaan merupakan showcase statis.

Untuk memperbaiki mutu visual, gunakan `reference-calibration.md`: amati referensi, buat test scene, bandingkan checkpoint, revisi aset/motion, lalu terima baseline setelah review. Ini bukan training/fine-tuning bobot model. Tidak perlu menyuplai video tambahan untuk menjalankan perbaikan kompatibilitas ini.
