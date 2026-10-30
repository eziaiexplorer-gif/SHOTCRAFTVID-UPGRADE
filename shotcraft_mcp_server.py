from pathlib import Path
import runpy,sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"mcp"))
if __name__=="__main__":runpy.run_path(str(Path(__file__).resolve().parent/"mcp/shotcraft_mcp_server.py"),run_name="__main__")
