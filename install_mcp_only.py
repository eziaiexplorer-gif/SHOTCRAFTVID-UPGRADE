from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parent
if not (r/"install.py").is_file():r=r.parent
if __name__=="__main__":
    if not (r/"install.py").is_file():raise SystemExit("Run install_mcp_only.py from the extracted bundle")
    raise SystemExit(subprocess.call([sys.executable,str(r/"install.py"),"--mcp-only",*sys.argv[1:]]))
