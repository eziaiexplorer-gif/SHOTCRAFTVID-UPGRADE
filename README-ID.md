# Shotcraft Local Kit 9.8.1 — audit kompatibilitas

Paket pendamping produksi video lokal untuk **Claude Code, Codex, dan OpenCode**. Berisi 12 skills, 12 peran agent, 5 MCP stdio, CLI, renderer Pillow/FFmpeg, dan komponen Remotion. Model AI tetap mengikuti pilihan di aplikasi agent; paket ini tidak menyertakan model AI atau langganan.

Versi ini memperbaiki installer, integrasi MCP, lokasi modul setelah instalasi, durasi, kontrol audio, jalur Remotion, dan pelaporan QA. Baca `AUDIT-ID.md` untuk bug, hasil pengujian, dan batasnya. Tidak ada jaminan bebas bug pada semua komputer atau penghematan token 95%.

## Persiapan

- Python **3.11+** dan FFmpeg/ffprobe tersedia di PATH
- Claude Code, Codex, atau OpenCode terpasang dan dikonfigurasi sendiri
- Engine Pillow: dependencies `requirements.txt`
- Remotion: Node.js/npm, dependencies proyek, dan browser Chromium yang didukung
- TTS online: provider, paket opsional, jaringan dan izin pengiriman naskah
- TTS offline: engine/model lokal terpasang; sampel WAV dan profil suara bukan model sintesis

Gunakan virtual environment agar dependencies tidak bercampur dengan program lain.

**Windows:**
```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python install.py --client all
```

**macOS / Linux:**
```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python install.py --client all
```

Ganti `all` dengan `claude`, `codex`, atau `opencode` bila hanya memakai satu. Jalur Python virtualenv disimpan dalam konfigurasi MCP, jadi pertahankan folder virtualenv setelah instalasi. Pakai `--upgrade` untuk upgrade dengan backup. `--dry-run` memeriksa tujuan tanpa memasang. `--install-deps` adalah alternatif pemasangan dependencies core ke interpreter yang sedang dipakai; tidak otomatis menginstal model/CLI/browser.

Untuk Edge TTS atau decoder OpenCV, pasang `requirements-optional.txt` dengan Python virtualenv yang sama. Jalankan `python doctor.py --strict` dari paket untuk pemeriksaan dependency. File `shotcraft-doctor.py` juga tersedia di direktori client sesudah instalasi.

## Lokasi instalasi

| Client | Skills | Agent/peran | Konfigurasi MCP |
|---|---|---|---|
| Claude Code | `~/.claude/skills` | `~/.claude/agents/*.md` | `~/.claude.json` |
| Codex | `~/.agents/skills` | `~/.codex/agents/*.toml` | `~/.codex/config.toml` |
| OpenCode | `~/.config/opencode/skills` | `~/.config/opencode/agents/*.md` | `opencode.json` atau `opencode.jsonc` di direktori tersebut |

Installer mengikuti CLAUDE_CONFIG_DIR, CODEX_HOME, dan XDG_CONFIG_HOME; tersedia override `--claude-dir`, `--codex-dir`, `--opencode-dir`. Dengan override Codex eksplisit, skills berada di `<codex-dir>/skills`; bila versi Codex Anda tidak mendeteksi lokasi itu, gunakan `--skills-dir ~/.agents/skills` untuk discovery global. MCP tetap menggunakan lokasi skills eksplisit yang dihasilkan.

Konfigurasi lain dipertahankan. Konfigurasi rusak ditolak, tidak diganti kosong. Upgrade menyimpan backup dan memulihkan file bila transaksi gagal. JSONC dinormalisasi ke JSON valid pada file yang sama; komentar asli tersedia di backup. `CLAUDE.md`/`AGENTS.md` global milik pengguna tidak ditimpa. Repo eksternal `--repo` tidak dimodifikasi.

MCP-only update: `python install_mcp_only.py --client all --upgrade`, setelah skills terpasang. Alias duplikat `shotcraft-pro` tidak ditambahkan; gunakan `shotcraft-director`.

## Pemakaian

Mulai ulang client setelah instalasi. Prompt sederhana cukup:

> Gunakan reels-director untuk membuat Reels 40 detik tentang cara kerja kulkas, visual cutaway yang jelas, narasi Indonesia, tanpa musik

Agent harus menyusun naskah/aset sesuai topik dan memeriksa fakta. CLI topic-only memakai heuristik/template dan bisa menghasilkan uraian generik; itu bukan riset ilmiah atau generator objek akurat untuk setiap topik.

Contoh render tanpa narasi/musik dari folder paket:
```sh
python shotcraft.py create "Uji visual sederhana" --workspace ./video-test --duration 6 --no-narration --no-bgm --engine pillow
```

- `--duration-policy fixed` adalah default: jumlah frame mengikuti durasi. Narasi terlalu panjang harus disingkat atau gagal jelas, bukan diam-diam memperpanjang video
- `--duration-policy audio`: durasi boleh mengikuti narasi
- `--no-narration`, `--no-bgm`, `--no-sfx`: kontrol terpisah; ketiganya menghasilkan audio hening
- `--tts-provider edge --allow-cloud`: sintesis online yang diizinkan, setelah `edge-tts` dipasang
- `--tts-mode offline`: tidak memilih layanan TTS cloud
- `--workflow-mode manual`: storyboard/contact sheet sebelum MP4
- `--allow-multi-style`: izinkan campuran keluarga visual; default menjaga satu keluarga

Engine Remotion membutuhkan `npm install` di workspace video. Versi paket Remotion seed dipin ke versi yang diuji. Browser dapat ditentukan dengan `SHOTCRAFT_BROWSER_EXECUTABLE`; jangan menyalin path Linux ke Windows. Concurrency default satu, dapat diatur lewat `SHOTCRAFT_CONCURRENCY` sesuai batas mesin. Error rinci disimpan di `qa/remotion-render.log`.

`rendered_needs_review` berarti render dan pemeriksaan otomatis selesai, **belum persetujuan publikasi**. Safe-zone edge scan bukan OCR, pemeriksaan semantik bukan fact-checker, dan perbandingan golden library bukan penilaian estetika video baru. Lakukan review visual/listening yang sebenarnya. `--visual-review-pass`/`--listening-pass` hanya boleh dicatat setelah review dilakukan.

## Referensi dan peningkatan visual

Panduan: `reels-motion/references/reference-calibration.md`.
```sh
python reels-motion/scripts/reference_contact_sheet.py referensi.mp4 --out ./study-baru --samples 12
```

Bandingkan aset, komposisi, motion dan timing pada checkpoint tetap, revisi satu aspek, lalu terima baseline baru setelah review. Ini kalibrasi resep/prompt/tes, **bukan training bobot model**. Video referensi tambahan boleh digunakan kemudian; tidak dibutuhkan untuk memperbaiki bug runtime saat ini.

## Batas yang masih berlaku

- Tes nyata dilakukan di Linux; Windows/macOS belum dieksekusi. Workflow CI lintas-OS disertakan, belum dijalankan jarak jauh
- Koneksi MCP diuji pada Claude Code/OpenCode; Codex CLI memuat config MCP. Tidak ada sesi model berbayar end-to-end yang dijalankan
- Tidak ada audisi provider TTS cloud atau model neural offline nyata dalam audit ini
- `--use-gpu`, `--frame-cache`, `--cloud-render` sebelumnya hanya flag tanpa implementasi; kini ditolak jelas, bukan dilaporkan bekerja
- Depth engine saat ini memakai heuristik gambar 2.5D, bukan model MiDaS/Depth-Anything
- Golden frames bawaan tidak cocok dengan seluruh hasil di lingkungan ini; baseline tidak ditimpa otomatis agar kegagalan terlihat
- `claude_shotcraft.html` adalah dokumen/showcase statis, bukan panel kontrol yang terhubung ke renderer
- Aset, voice reference, dan atribusi yang dibawa ZIP sumber dipertahankan; audit teknis tidak memverifikasi izin komersial semua aset

## Tes
```sh
python -m unittest discover -s tests -v
node reels-continuity-lab/scripts/test-motion-math.mjs
```
