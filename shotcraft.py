#!/usr/bin/env python3
"""
Shotcraft Pro v9.7.0 — Unified Developer CLI (`shotcraft.py`).

Implements Audit Fixes F04, F12, F15 & T18:
- `shotcraft create "Cara kerja mesin potong rumput" --style auto-context --engine auto --mode draft`
- `shotcraft draft "Cara kerja mesin potong rumput" --workspace ./ws_mower`
- `shotcraft critique ./ws_mower`
- `shotcraft preview <workspace> --frame 45 [--open] [--watch] [--engine auto]`
- `shotcraft template list`
- `shotcraft template search <query>` (Fully implemented! Searches templates_catalog.json, continuity_lab, and opus_craft)
- `shotcraft template install <template_name> --workspace <dir>`
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
_PATH_CONFIG = HERE / 'shotcraft-paths.json'
if os.environ.get('SHOTCRAFT_SKILLS_DIR'):
    HERE = Path(os.environ['SHOTCRAFT_SKILLS_DIR']).expanduser().resolve()
elif _PATH_CONFIG.is_file():
    HERE = Path(json.loads(_PATH_CONFIG.read_text(encoding='utf-8'))['skills_dir'])


# Installed skill engines are siblings; shared style definitions live with templates.
for module_dir in [HERE / 'reels-templates/scripts', HERE / 'reels-narration/scripts']:
    sys.path.insert(0, str(module_dir))


def cmd_create(args) -> int:
    slug = "".join(c if c.isalnum() else "_" for c in args.topic.lower()).strip("_")[:28] or "reel"
    ws = Path(args.workspace or f"./workspace_{slug}").expanduser().resolve()
    cmd = [
        sys.executable,
        str(HERE / "reels-production" / "scripts" / "one_shot_produce.py"),
        "--workspace", str(ws),
        "--topic", args.topic,
        "--style", args.style,
        "--engine", args.engine,
        "--mode", args.mode,
        "--duration", str(args.duration),
        "--fps", str(args.fps),
        "--aspect", args.aspect,
        "--ab-variants", str(args.ab_variants),
    ]
    if args.language:
        cmd.extend(["--language", args.language])
    if args.domain:
        cmd.extend(["--domain", args.domain])
    if args.script:
        cmd.extend(["--script", args.script])
    if getattr(args, "output_mp4", None):
        cmd.extend(["--output-mp4", args.output_mp4])
    if getattr(args, "raw_video", None):
        cmd.extend(["--raw-video", args.raw_video])
    if getattr(args, "voiceover", None):
        cmd.extend(["--voiceover", args.voiceover])
    if getattr(args, "voice_folder", None):
        cmd.extend(["--voice-folder", args.voice_folder])
    if getattr(args, "voice_profile", None):
        cmd.extend(["--voice-profile", args.voice_profile])
    if getattr(args, "tts_provider", None):
        cmd.extend(["--tts-provider", args.tts_provider])
    if getattr(args, "tts_mode", None):
        cmd.extend(["--tts-mode", args.tts_mode])
    if getattr(args, "speaker_wav", None):
        cmd.extend(["--speaker-wav", args.speaker_wav])
    for name in ['no_bgm', 'no_sfx', 'allow_cloud']:
        if getattr(args, name, False): cmd.append('--'+name.replace('_','-'))
    if getattr(args, 'duration_policy', None): cmd.extend(['--duration-policy', args.duration_policy])
    if getattr(args, "no_narration", None):
        cmd.append("--no-narration")
    if getattr(args, "strict_provider", None):
        cmd.append("--strict-provider")
    if getattr(args, "coqui_model", None):
        cmd.extend(["--coqui-model", args.coqui_model])
    if getattr(args, "emotion", None):
        cmd.extend(["--emotion", args.emotion])
    if getattr(args, "sfx_pack", None):
        cmd.extend(["--sfx-pack", args.sfx_pack])
    if getattr(args, "bgm_track", None):
        cmd.extend(["--bgm-track", args.bgm_track])
    if getattr(args, "workflow_mode", None):
        cmd.extend(["--workflow-mode", args.workflow_mode])
    if getattr(args, "video_crop", None):
        cmd.extend(["--video-crop", args.video_crop])
    if getattr(args, "caption_style", None):
        cmd.extend(["--caption-style", args.caption_style])
    for _flag_attr, _cli_flag in [
        ("font_family", "--font-family"),
        ("accent_color", "--accent-color"),
        ("headline_text", "--headline-text"),
        ("subcopy_text", "--subcopy-text"),
        ("caption_text", "--caption-text"),
        ("eyebrow_text", "--eyebrow-text"),
        ("caption_highlight_color", "--caption-highlight-color"),
        ("archetype", "--archetype"),
        ("broll_mode", "--broll-mode"),
    ]:
        val = getattr(args, _flag_attr, None)
        if val:
            cmd.extend([_cli_flag, str(val)])
    if getattr(args, "caption_y", 0) and int(args.caption_y) > 0:
        cmd.extend(["--caption-y", str(args.caption_y)])
    if args.title_badge:
        cmd.extend(["--title-badge", args.title_badge])
    if args.no_badge:
        cmd.append("--no-badge")
    if args.allow_multi_style:
        cmd.append("--allow-multi-style")
    if getattr(args, "lock_single_style", None):
        cmd.append("--lock-single-style")
    if args.parallel_scenes:
        cmd.append("--parallel-scenes")
    if args.use_gpu:
        cmd.append("--use-gpu")
    if args.verbose:
        cmd.append("--verbose")
    if getattr(args, "listening_pass", None):
        cmd.append("--listening-pass")
    return subprocess.call(cmd)


def cmd_edit_media(args) -> int:
    media_file = getattr(args, "video", None) or getattr(args, "voiceover", None) or ""
    slug = "".join(c if c.isalnum() else "_" for c in Path(media_file or "media").stem.lower()).strip("_")[:24] or "edit"
    ws = Path(args.workspace or f"./workspace_{slug}").expanduser().resolve()
    cmd = [
        sys.executable,
        str(HERE / "reels-auto-editor" / "scripts" / "auto_media_pipeline.py"),
        "--out-dir", str(ws),
        "--style", args.style,
        "--caption-style", args.caption_style,
        "--aspect", args.aspect,
        "--video-crop", getattr(args, "video_crop", "cover"),
        "--render-mp4",
    ]
    if getattr(args, "video", None):
        cmd.extend(["--raw-video", args.video])
    if getattr(args, "voiceover", None):
        cmd.extend(["--voiceover", args.voiceover])
    if getattr(args, "transcript", None):
        cmd.extend(["--transcript", args.transcript])
    if getattr(args, "topic", None):
        cmd.extend(["--topic", args.topic])
    if getattr(args, "bgm_track", None):
        cmd.extend(["--bgm-track", args.bgm_track])
    if getattr(args, "sfx_pack", None):
        cmd.extend(["--sfx-pack", args.sfx_pack])
    if getattr(args, "output_mp4", None):
        cmd.extend(["--output-mp4", args.output_mp4])
    for _flag_attr, _cli_flag in [
        ("font_family", "--font-family"),
        ("accent_color", "--accent-color"),
        ("headline_text", "--headline-text"),
        ("subcopy_text", "--subcopy-text"),
        ("caption_text", "--caption-text"),
        ("eyebrow_text", "--eyebrow-text"),
        ("caption_highlight_color", "--caption-highlight-color"),
        ("archetype", "--archetype"),
        ("broll_mode", "--broll-mode"),
    ]:
        val = getattr(args, _flag_attr, None)
        if val:
            cmd.extend([_cli_flag, str(val)])
    if getattr(args, "caption_y", 0) and int(args.caption_y) > 0:
        cmd.extend(["--caption-y", str(args.caption_y)])
    return subprocess.call(cmd)


def cmd_ingest_raw(args) -> int:
    raw_dir = Path(args.raw_dir).expanduser().resolve()
    slug = "".join(c if c.isalnum() else "_" for c in raw_dir.name.lower()).strip("_")[:24] or "ingest"
    ws = Path(args.workspace or f"./workspace_ingest_{slug}").expanduser().resolve()
    cmd = [
        sys.executable,
        str(HERE / "reels-auto-editor" / "scripts" / "auto_media_pipeline.py"),
        "--raw-dir", str(raw_dir),
        "--out-dir", str(ws),
        "--style", args.style,
        "--aspect", args.aspect,
    ]
    if args.watch:
        cmd.append("--watch")
    cmd.extend(["--poll-sec", str(args.poll_sec)])
    return subprocess.call(cmd)


def cmd_draft(args) -> int:
    slug = "".join(c if c.isalnum() else "_" for c in args.topic.lower()).strip("_")[:28] or "reel"
    ws = Path(args.workspace or f"./workspace_{slug}").expanduser().resolve()
    cmd = [
        sys.executable,
        str(HERE / "reels-qa" / "scripts" / "storyboard_critique.py"),
        "draft",
        "--workspace", str(ws),
        "--topic", args.topic,
        "--style", args.style,
        "--duration", str(args.duration),
        "--fps", str(args.fps),
    ]
    if args.language:
        cmd.extend(["--language", args.language])
    return subprocess.call(cmd)


def cmd_critique(args) -> int:
    ws = Path(args.workspace).expanduser().resolve()
    cmd = [
        sys.executable,
        str(HERE / "reels-qa" / "scripts" / "storyboard_critique.py"),
        "critique",
        "--workspace", str(ws),
    ]
    return subprocess.call(cmd)


def _open_file_in_viewer(filepath: Path) -> dict:
    """F15 / T18: Opens rendered preview PNG in system viewer or reports headless status."""
    if not filepath.is_file():
        return {"opened": False, "reason": f"File not found: {filepath}"}
    if sys.platform.startswith("win"):
        try:
            os.startfile(str(filepath))  # type: ignore[attr-defined]
            return {"opened": True, "viewer": "windows-startfile"}
        except Exception as exc:
            return {"opened": False, "reason": str(exc)}
    if sys.platform == "darwin" and shutil.which("open"):
        subprocess.Popen(["open", str(filepath)], stdin=subprocess.DEVNULL)
        return {"opened": True, "viewer": "macos-open"}
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", str(filepath)], stdin=subprocess.DEVNULL)
            return {"opened": True, "viewer": "xdg-open"}
        webbrowser.open(filepath.as_uri())
        return {"opened": True, "viewer": "webbrowser"}
    return {
        "opened": False,
        "viewer": "headless-env",
        "reason": "No GUI DISPLAY detected in current environment; preview PNG saved on disk.",
        "preview_png": str(filepath),
    }


def cmd_preview(args) -> int:
    ws = Path(args.workspace).expanduser().resolve()
    render_script = HERE / "reels-templates" / "scripts" / "smart_render.py"

    if args.serve:
        cmd = [
            sys.executable,
            str(render_script),
            "--workspace", str(ws),
            "--engine", args.engine,
            "--serve-preview", str(args.port),
        ]
        return subprocess.call(cmd)

    def _render_once() -> tuple[int, dict]:
        res = subprocess.run(
            [
                sys.executable,
                str(render_script),
                "--workspace", str(ws),
                "--engine", args.engine,
                "--preview-frame", str(args.frame),
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            data = json.loads(res.stdout.strip()) if res.stdout.strip().startswith("{") else {"stdout": res.stdout.strip()}
        except Exception:
            data = {"stdout": res.stdout.strip()}
        return res.returncode, data

    rc, payload = _render_once()
    if args.open and payload.get("preview_png"):
        payload["open_viewer"] = _open_file_in_viewer(Path(payload["preview_png"]))

    if not args.watch:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return rc

    # F15 / T18: `--watch` polls `timeline.json` and `src/MainReel.tsx` and re-renders automatically on modification
    max_polls = int(os.environ.get("SHOTCRAFT_WATCH_MAX_POLLS", "0" if sys.stdin.isatty() else "5"))
    poll_interval = float(os.environ.get("SHOTCRAFT_WATCH_INTERVAL_SEC", "0.8"))
    watched_files = [ws / "timeline.json", ws / "src" / "MainReel.tsx"]

    def _get_mtimes():
        return {str(f): (f.stat().st_mtime if f.is_file() else 0.0) for f in watched_files}

    last_mtimes = _get_mtimes()
    rerenders = 0
    payload["watch_mode"] = True
    payload["watched_files"] = list(last_mtimes.keys())
    print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)

    polls = 0
    try:
        while True:
            time.sleep(poll_interval)
            polls += 1
            cur_mtimes = _get_mtimes()
            if cur_mtimes != last_mtimes:
                last_mtimes = cur_mtimes
                rerenders += 1
                _, new_payload = _render_once()
                new_payload["watch_event"] = "rerendered_on_change"
                new_payload["rerender_count"] = rerenders
                print(json.dumps(new_payload, indent=2, ensure_ascii=False), flush=True)
            if max_polls > 0 and polls >= max_polls:
                break
    except KeyboardInterrupt:
        pass
    return 0


def cmd_template(args) -> int:
    cat_path = HERE / "reels-templates" / "blueprints" / "templates_catalog.json"
    cont_path = HERE / "reels-continuity-lab" / "catalog.json"
    style_path = HERE / "mcp" / "core" / "style_map.py"

    data = json.loads(cat_path.read_text(encoding="utf-8")) if cat_path.is_file() else {}
    if args.tpl_action == "create-style":
        sys.path.insert(0, str(HERE / "mcp" / "core"))
        import style_map as sm_mod
        res_cs = sm_mod.save_user_custom_style(
            name=args.name or "my-custom-style",
            base_style=getattr(args, "base_style", "kaca-gelap"),
            world=getattr(args, "world", ""),
            caption_style=getattr(args, "caption_style", ""),
            accent_color=getattr(args, "accent_color", ""),
            font_family=getattr(args, "font_family", ""),
            bgm_track=getattr(args, "bgm_track", ""),
            sfx_pack=getattr(args, "sfx_pack", ""),
            description=getattr(args, "description", ""),
        )
        print(json.dumps(res_cs, indent=2, ensure_ascii=False))
        return 0

    if args.tpl_action == "list":
        sys.path.insert(0, str(HERE / "mcp" / "core"))
        import style_map as sm_mod
        print(
            json.dumps(
                {
                    "ok": True,
                    "version": "9.8.0",
                    "total_valid_style_choices": len(sm_mod.ALL_VALID_STYLE_CHOICES),
                    "total_procedural_and_custom_styles": len(sm_mod.OPUS_55_PROCEDURAL_MODES),
                    "style_families": sm_mod.STYLE_FAMILIES,
                    "procedural_and_custom_styles": sm_mod.OPUS_55_PROCEDURAL_MODES,
                    "caption_presets_count": len(sm_mod.VALID_CAPTION_STYLES),
                    "caption_presets": sm_mod.VALID_CAPTION_STYLES,
                    "templates": data,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.tpl_action == "search":
        # F15 / T18: Fully implemented `template search <query>`
        query = (args.name or "").strip().lower()
        if query == "kinetic-fact-story" and len(sys.argv) <= 3:
            query = ""
        sys.path.insert(0, str(HERE / "mcp" / "core"))
        import style_map as sm_mod

        matches = []
        # 1. Search 4 Reference Style Families
        for fam_id, fam_spec in sm_mod.STYLE_FAMILIES.items():
            blob = f"{fam_id} {fam_spec.get('description', '')} {' '.join(fam_spec.get('best_for', []))}".lower()
            if not query or query in blob or any(w in blob for w in query.split()):
                matches.append({
                    "kind": "style-family",
                    "id": fam_id,
                    "benchmark_ref": fam_spec.get("benchmark_ref"),
                    "description": fam_spec.get("description"),
                    "best_for": fam_spec.get("best_for"),
                })

        # 2. Search Blueprint Templates Catalog
        tpl_items = data.get("templates", data) if isinstance(data, dict) else data
        if isinstance(tpl_items, dict):
            for t_id, t_val in tpl_items.items():
                blob = f"{t_id} {json.dumps(t_val, ensure_ascii=False)}".lower()
                if not query or query in blob or any(w in blob for w in query.split()):
                    matches.append({"kind": "blueprint-template", "id": t_id, "spec": t_val})
        elif isinstance(tpl_items, list):
            for t_val in tpl_items:
                blob = json.dumps(t_val, ensure_ascii=False).lower()
                if not query or query in blob or any(w in blob for w in query.split()):
                    matches.append({"kind": "blueprint-template", "id": t_val.get("id") or t_val.get("name"), "spec": t_val})

        # 3. Search Continuity Lab Catalog if present
        if cont_path.is_file():
            try:
                c_data = json.loads(cont_path.read_text(encoding="utf-8"))
                c_list = c_data.get("recipes", c_data) if isinstance(c_data, dict) else c_data
                if isinstance(c_list, list):
                    for rec in c_list:
                        blob = json.dumps(rec, ensure_ascii=False).lower()
                        if not query or query in blob or any(w in blob for w in query.split()):
                            matches.append({"kind": "continuity-recipe", "id": rec.get("id"), "spec": rec})
            except Exception:
                pass

        # 4. Search all 114 Opus 5.5, Staikhouse #gaya, Awesome Claude Video Skills, & User Custom Styles
        for m_id, m_spec in sm_mod.OPUS_55_PROCEDURAL_MODES.items():
            blob = f"{m_id} {json.dumps(m_spec, ensure_ascii=False)}".lower()
            if not query or query in blob or any(w in blob for w in query.split()):
                matches.append({"kind": "motion-or-visual-style", "id": m_id, "spec": m_spec})

        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "search",
                    "query": query,
                    "count": len(matches),
                    "matches": matches,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.tpl_action == "install":
        ws = Path(args.workspace or f"./workspace_{args.name}").expanduser().resolve()
        cmd = [
            sys.executable,
            str(HERE / "reels-templates" / "scripts" / "scaffold_project.py"),
            "--workspace", str(ws),
            "--template", args.name,
            "--overwrite",
        ]
        return subprocess.call(cmd)
    return 0




def cmd_voice(args) -> int:
    vb_script = HERE / "reels-narration" / "scripts" / "voice_bank.py"
    act = args.voice_action
    cmd = [sys.executable, str(vb_script), act]
    if act == "list" and getattr(args, "bundled_only", False):
        cmd.append("--bundled-only")
    elif act == "recommend":
        cmd.extend(["--style", args.style, "--topic", args.topic or "", "--language", args.language or "id-ID"])
    elif act == "import":
        if not args.target or not args.name:
            print(json.dumps({"ok": False, "error": "Usage: shotcraft.py voice import <audio_file> --name <profile_name> [--ref-text '...']"}))
            return 2
        cmd.extend([args.target, "--name", args.name])
        if args.ref_text:
            cmd.extend(["--ref-text", args.ref_text])
    elif act in ("extract", "extract-video"):
        if not args.target or not args.name:
            print(json.dumps({"ok": False, "error": "Usage: shotcraft.py voice extract-video <video.mp4> --name <profile_name> [--start 0.5] [--duration 8.5]"}))
            return 2
        cmd = [sys.executable, str(vb_script), "extract-video", args.target, "--name", args.name, "--start", str(args.start), "--duration", str(args.duration)]
        if args.ref_text:
            cmd.extend(["--ref-text", args.ref_text])
    elif act == "fetch-preview":
        if not args.target:
            print(json.dumps({"ok": False, "error": "Usage: shotcraft.py voice fetch-preview <voice_name_or_id> [--preview-url <url>]"}))
            return 2
        cmd.append(args.target)
        if args.preview_url:
            cmd.extend(["--preview-url", args.preview_url])
    elif act == "resolve-folder":
        if not args.target:
            print(json.dumps({"ok": False, "error": "Usage: shotcraft.py voice resolve-folder <folder_path>"}))
            return 2
        cmd.append(args.target)
    elif act == "sync-voicestudio":
        cmd.extend(["--url", args.url])
    return subprocess.call(cmd)


def cmd_plan(args) -> int:
    """Hybrid Auto vs Manual planner: outputs structured options for Claude Code / User before rendering."""
    slug = "".join(c if c.isalnum() else "_" for c in args.topic.lower()).strip("_")[:28] or "reel"
    ws = Path(args.workspace or f"./workspace_{slug}").expanduser().resolve()
    cmd = [
        sys.executable,
        str(HERE / "reels-production" / "scripts" / "one_shot_produce.py"),
        "--workspace", str(ws),
        "--topic", args.topic,
        "--style", args.style,
        "--voice-profile", args.voice_profile,
        "--workflow-mode", args.workflow_mode,
    ]
    if args.language:
        cmd.extend(["--language", args.language])
    return subprocess.call(cmd)


def main():
    p = argparse.ArgumentParser(prog="shotcraft", description="Shotcraft Pro v9.7.0 Unified CLI")
    sub = p.add_subparsers(dest="subcmd", required=True)

    p_create = sub.add_parser("create", help="Create a complete Reel MP4 from a topic or script")
    p_create.add_argument("topic", help="Topic e.g. 'Cara kerja mesin potong rumput'")
    p_create.add_argument("--workspace", help="Target workspace directory (auto-named if omitted)")
    p_create.add_argument("--output-mp4", help="Optional output MP4 path")
    p_create.add_argument("--style", default="auto-context")
    p_create.add_argument("--engine", choices=["auto", "pillow", "cinema-pil", "remotion"], default="auto")
    p_create.add_argument("--mode", choices=["draft", "final"], default="draft")
    p_create.add_argument("--language", default="", help="Optional language code: id-ID or en-US")
    p_create.add_argument("--domain", default="", help="Optional domain override")
    p_create.add_argument("--script", help="Optional path to script file")
    p_create.add_argument("--raw-video", help="Optional raw video file (.mp4/.mov) to auto-cut and edit")
    p_create.add_argument("--voiceover", help="Optional recorded voiceover file (.wav/.mp3/.m4a) to edit and sync")
    p_create.add_argument("--voice-folder", help="Option B: Offline folder with voiceover audio (single full file or per-scene 01.wav..06.wav)")
    p_create.add_argument("--voice-profile", default="auto", help="Option A: Bundled voice profile (auto, bian, zan, denas, nesah_paramitha, bayu, selina, abysa, defasyalala, istiqomah, kak_ceria)")
    p_create.add_argument("--tts-mode", default="auto", choices=["auto", "online", "offline"], help="Online/Offline TTS routing mode")
    p_create.add_argument("--tts-provider", default="edge", help="TTS/cloning provider (auto, voicestudio, f5-tts, coqui, edge, elevenlabs, local-synth)")
    p_create.add_argument("--speaker-wav", help="Optional custom reference .wav for zero-shot voice cloning")
    p_create.add_argument("--no-bgm", action="store_true")
    p_create.add_argument("--no-sfx", action="store_true")
    p_create.add_argument("--allow-cloud", action="store_true")
    p_create.add_argument("--duration-policy", choices=["fixed", "audio"], default="fixed")
    p_create.add_argument("--no-narration", action="store_true", help="Disable TTS narration generation")
    p_create.add_argument("--strict-provider", action="store_true", help="Fail if preferred TTS provider unavailable")
    p_create.add_argument("--coqui-model", help="Coqui TTS model name")
    p_create.add_argument("--emotion", choices=["excited","warm","urgent","calm","energetic","serious","friendly"], help="TTS emotion style")
    p_create.add_argument("--sfx-pack", help="SFX pack name")
    p_create.add_argument("--bgm-track", help="BGM track filename")
    p_create.add_argument("--workflow-mode", default="auto", choices=["auto", "manual", "ask"], help="Hybrid workflow: 'auto' (full render), 'manual' (stage storyboard + contact sheet first), or 'ask' (show interactive choices)")
    p_create.add_argument("--video-crop", default="cover", choices=["cover", "blur-pad"])
    p_create.add_argument("--duration", type=float, default=24.0)
    p_create.add_argument("--fps", type=int, default=30)
    p_create.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1", "4:5", "2:3"])
    p_create.add_argument("--caption-style", default="", help="Single caption style, comma-separated per-scene styles, or 'none'")
    p_create.add_argument("--font-family", default="", help="Custom font family (sans, serif, mono, inter-black, bebas-bold, anton, poppins-bold, garamond-bd-it, unifraktur, script)")
    p_create.add_argument("--accent-color", default="", help="Custom hex accent color e.g. '#A3E635' or comma-separated per scene")
    p_create.add_argument("--headline-text", default="", help="Custom headline text (single or '|'-separated per scene)")
    p_create.add_argument("--subcopy-text", default="", help="Custom subcopy/card text (single or '|'-separated per scene)")
    p_create.add_argument("--caption-text", default="", help="Custom caption/subtitle text (single or '|'-separated per scene)")
    p_create.add_argument("--eyebrow-text", default="", help="Custom top eyebrow/kicker text (single or '|'-separated per scene)")
    p_create.add_argument("--caption-y", type=int, default=0, help="Custom vertical Y coordinate for captions (e.g. 1350, 1465, 260)")
    p_create.add_argument("--caption-highlight-color", default="", help="Custom hex color for active caption word highlight e.g. '#FACC15'")
    p_create.add_argument("--archetype", default="", help="Custom talking-head archetype (single or comma-separated)")
    p_create.add_argument("--broll-mode", default="auto", choices=["auto", "fullscreen", "pip", "none"], help="B-roll display mode")
    p_create.add_argument("--ab-variants", type=int, default=1)
    p_create.add_argument("--title-badge", default="")
    p_create.add_argument("--no-badge", action="store_true")
    p_create.add_argument("--allow-multi-style", action="store_true")
    p_create.add_argument("--lock-single-style", action="store_true", default=False, help="Keep coherent style family across scenes (default False — allow style variety)")
    p_create.add_argument("--parallel-scenes", action="store_true")
    p_create.add_argument("--use-gpu", action="store_true")
    p_create.add_argument("--verbose", action="store_true")
    p_create.add_argument("--listening-pass", action="store_true", default=False, help="Approve human listening review gate (set listening_pass=True)")

    p_draft = sub.add_parser("draft", help="Generate domain-accurate storyboard + contact sheet PNG")
    p_draft.add_argument("topic", help="Topic e.g. 'Cara kerja mesin potong rumput'")
    p_draft.add_argument("--workspace", help="Target workspace directory")
    p_draft.add_argument("--style", default="auto-context")
    p_draft.add_argument("--language", default="")
    p_draft.add_argument("--duration", type=float, default=24.0)
    p_draft.add_argument("--fps", type=int, default=30)

    p_crit = sub.add_parser("critique", help="Run automated semantic & visual critique")
    p_crit.add_argument("workspace", help="Target workspace directory")

    p_prev = sub.add_parser("preview", help="Render an instant frame PNG or launch live preview server")
    p_prev.add_argument("workspace", help="Workspace directory")
    p_prev.add_argument("--frame", type=int, default=45, help="Frame number to preview as PNG")
    p_prev.add_argument("--engine", choices=["auto", "pillow", "cinema-pil", "remotion"], default="auto")
    p_prev.add_argument("--serve", action="store_true", help="Launch live browser frame scrubber")
    p_prev.add_argument("--port", type=int, default=8765)
    p_prev.add_argument("--open", action="store_true", help="Open rendered still PNG in default viewer (F15)")
    p_prev.add_argument("--watch", action="store_true", help="Watch timeline.json and auto-rerender preview frame (F15)")

    p_tpl = sub.add_parser("template", help="Browse, search, install, or create custom Shotcraft Pro templates & styles")
    p_tpl.add_argument("tpl_action", choices=["list", "install", "search", "create-style"])
    p_tpl.add_argument("name", nargs="?", default="")
    p_tpl.add_argument("--workspace", help="Target workspace for template install")
    p_tpl.add_argument("--base-style", default="kaca-gelap", help="Base style to clone when using create-style")
    p_tpl.add_argument("--world", default="", help="Custom world background when using create-style")
    p_tpl.add_argument("--caption-style", default="", help="Default caption style for your custom style")
    p_tpl.add_argument("--accent-color", default="", help="Default hex accent color for your custom style")
    p_tpl.add_argument("--font-family", default="", help="Default font family for your custom style")
    p_tpl.add_argument("--bgm-track", default="", help="Default BGM track for your custom style")
    p_tpl.add_argument("--sfx-pack", default="", help="Default SFX pack for your custom style")
    p_tpl.add_argument("--description", default="", help="Description of your custom style")

    p_ev = sub.add_parser("edit-video", help="Auto-cut and edit a raw video (.mp4/.mov) with optional voiceover, subtitles, transitions, and BGM")
    p_ev.add_argument("video", help="Path to raw video file (.mp4/.mov/.mkv)")
    p_ev.add_argument("--voiceover", help="Optional recorded voiceover file (.wav/.mp3/.m4a) to replace or drive timing")
    p_ev.add_argument("--transcript", help="Optional .txt/.srt transcript file or script text")
    p_ev.add_argument("--topic", default="", help="Optional topic description")
    p_ev.add_argument("--workspace", help="Target workspace directory")
    p_ev.add_argument("--output-mp4", help="Optional output MP4 path")
    p_ev.add_argument("--style", default="", help="Any style ID (e.g. kaca-gelap, arang-lime, paper-motion, talking-head, cutaway-turbofan)")
    p_ev.add_argument("--caption-style", default="", help="Any caption preset (e.g. xml-text1-gold-bevel, mogrt-20-sliding-lime, slide-up, neon, none)")
    p_ev.add_argument("--font-family", default="")
    p_ev.add_argument("--accent-color", default="")
    p_ev.add_argument("--headline-text", default="")
    p_ev.add_argument("--subcopy-text", default="")
    p_ev.add_argument("--caption-text", default="")
    p_ev.add_argument("--eyebrow-text", default="")
    p_ev.add_argument("--caption-y", type=int, default=0)
    p_ev.add_argument("--caption-highlight-color", default="")
    p_ev.add_argument("--archetype", default="")
    p_ev.add_argument("--broll-mode", default="auto", choices=["auto", "fullscreen", "pip", "none"])
    p_ev.add_argument("--video-crop", default="cover", choices=["cover", "blur-pad"])
    p_ev.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1", "4:5", "2:3"])
    p_ev.add_argument("--bgm-track", default="")
    p_ev.add_argument("--sfx-pack", default="")

    p_evo = sub.add_parser("edit-voiceover", help="Auto-cut a recorded voiceover (.wav/.mp3/.m4a), sync word captions, and generate 3D/Cutaway/Opus or raw-video visuals")
    p_evo.add_argument("voiceover", help="Path to recorded voiceover audio (.wav/.mp3/.m4a)")
    p_evo.add_argument("--video", help="Optional raw video file (.mp4/.mov) to use as visual B-roll")
    p_evo.add_argument("--transcript", help="Optional .txt/.srt transcript file or script text")
    p_evo.add_argument("--topic", default="", help="Topic description to drive 3D/Cutaway/Opus visuals")
    p_evo.add_argument("--workspace", help="Target workspace directory")
    p_evo.add_argument("--output-mp4", help="Optional output MP4 path")
    p_evo.add_argument("--style", default="", help="Any style ID (e.g. kaca-gelap, arang-lime, paper-motion, ref3-cutaway-mechanism)")
    p_evo.add_argument("--caption-style", default="", help="Any caption preset (e.g. xml-text1-gold-bevel, mogrt-20-sliding-lime, slide-up, neon, none)")
    p_evo.add_argument("--font-family", default="")
    p_evo.add_argument("--accent-color", default="")
    p_evo.add_argument("--headline-text", default="")
    p_evo.add_argument("--subcopy-text", default="")
    p_evo.add_argument("--caption-text", default="")
    p_evo.add_argument("--eyebrow-text", default="")
    p_evo.add_argument("--caption-y", type=int, default=0)
    p_evo.add_argument("--caption-highlight-color", default="")
    p_evo.add_argument("--archetype", default="")
    p_evo.add_argument("--broll-mode", default="auto", choices=["auto", "fullscreen", "pip", "none"])
    p_evo.add_argument("--video-crop", default="cover", choices=["cover", "blur-pad"])
    p_evo.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1", "4:5", "2:3"])
    p_evo.add_argument("--bgm-track", default="")
    p_evo.add_argument("--sfx-pack", default="")

    p_ir = sub.add_parser("ingest-raw", help="Scan a raw video folder and auto-ingest talking-head footage through the talking-head editing pipeline")
    p_ir.add_argument("raw_dir", help="Folder containing raw .mp4/.mov/.mkv/.webm talking-head videos to ingest")
    p_ir.add_argument("--workspace", help="Target workspace directory")
    p_ir.add_argument("--style", default="auto-context")
    p_ir.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1", "4:5", "2:3"])
    p_ir.add_argument("--watch", action="store_true", help="Keep watching for new files dropped into the folder")
    p_ir.add_argument("--poll-sec", type=float, default=5.0, help="Poll interval in seconds when --watch is enabled")

    p_voice = sub.add_parser("voice", help="Manage bundled Voice Bank (14 local .wav samples + 46 profiles), extract voice from video, or inspect offline voice folders")
    p_voice.add_argument("voice_action", choices=["list", "recommend", "import", "extract", "extract-video", "fetch-preview", "resolve-folder", "sync-voicestudio"])
    p_voice.add_argument("target", nargs="?", default="", help="Target audio/video file, folder, or voice ID")
    p_voice.add_argument("--name", default="", help="Profile name when importing or extracting a voice")
    p_voice.add_argument("--ref-text", default="", help="Transcript spoken in the reference audio")
    p_voice.add_argument("--style", default="ref3-cutaway-mechanism")
    p_voice.add_argument("--topic", default="")
    p_voice.add_argument("--language", default="id-ID")
    p_voice.add_argument("--start", type=float, default=0.5)
    p_voice.add_argument("--duration", type=float, default=8.5)
    p_voice.add_argument("--preview-url", default="")
    p_voice.add_argument("--url", default="http://localhost:3900", help="VoiceStudio server URL for sync-voicestudio")
    p_voice.add_argument("--bundled-only", action="store_true")

    p_plan = sub.add_parser("plan", help="Hybrid Auto vs Manual Planner: inspect recommended style, voice profile, and storyboard options before rendering")
    p_plan.add_argument("topic", help="Topic e.g. 'Cara kerja mesin potong rumput'")
    p_plan.add_argument("--workspace", help="Target workspace directory")
    p_plan.add_argument("--style", default="auto-context")
    p_plan.add_argument("--voice-profile", default="auto")
    p_plan.add_argument("--language", default="")
    p_plan.add_argument("--workflow-mode", default="ask", choices=["ask", "manual", "auto"])

    a = p.parse_args()
    if a.subcmd == "create":
        return cmd_create(a)
    if a.subcmd == "voice":
        return cmd_voice(a)
    if a.subcmd == "plan":
        return cmd_plan(a)
    if a.subcmd == "ingest-raw":
        return cmd_ingest_raw(a)
    if a.subcmd in ("edit-video", "edit-voiceover"):
        return cmd_edit_media(a)
    if a.subcmd == "draft":
        return cmd_draft(a)
    if a.subcmd == "critique":
        return cmd_critique(a)
    if a.subcmd == "preview":
        return cmd_preview(a)
    if a.subcmd == "template":
        if a.tpl_action == "install" and not a.name:
            a.name = "kinetic-fact-story"
        return cmd_template(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
