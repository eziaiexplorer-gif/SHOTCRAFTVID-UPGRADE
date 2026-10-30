# Validation for 9.8.1

Current evidence and limitations are in AUDIT-ID.md. This supersedes claims in the uploaded package's historical validation/documentation.

Reproducible offline checks:

```sh
python -m unittest discover -s tests -v
node reels-continuity-lab/scripts/test-motion-math.mjs
python doctor.py --strict
```

Seventeen tests passed in Linux with Python 3.12.14. Claude/OpenCode MCP health checks passed; Codex CLI parsed the configuration. Pillow and Remotion smoke renders passed exact technical checks. No real cloud TTS audition, local neural voice inference, Windows/macOS execution, or paid-agent session was performed. Missing/regressed golden frames do not count as passed. Successful rendering remains distinct from visual/listening approval.
