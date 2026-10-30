#!/usr/bin/env python3
"""Transactional, offline installer for Claude Code, Codex and OpenCode."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11+ is required. No files were installed.')
import tomllib

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
BUNDLE_VERSION = MANIFEST['version']
SKILLS = MANIFEST['skills']
AGENTS = MANIFEST['agents']
MCP_SERVERS = MANIFEST['mcp_servers']
BEGIN = '# BEGIN SHOTCRAFT MANAGED CONFIG'
END = '# END SHOTCRAFT MANAGED CONFIG'


def read_json_config(path):
    """Parse JSON/JSONC without treating comments inside quoted strings as comments."""
    if not path.exists():
        return {}
    source = path.read_text(encoding='utf-8-sig')
    out = []; i = 0; quoted = False; escaped = False
    while i < len(source):
        c = source[i]
        if quoted:
            out.append(c)
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
            i += 1; continue
        if c == '"': quoted = True
        if source[i:i+2] == '//':
            end = source.find('\n', i); i = len(source) if end < 0 else end; continue
        if source[i:i+2] == '/*':
            end = source.find('*/', i+2)
            if end < 0: raise ValueError(f'Unterminated JSONC comment: {path}')
            out.append(' '); i = end+2; continue
        out.append(c); i += 1
    source = ''.join(out); out = []; quoted = False; escaped = False
    for i,c in enumerate(source):
        if quoted:
            out.append(c)
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
            continue
        if c == '"': quoted = True
        if c == ',' and source[i+1:].lstrip().startswith(('}', ']')): continue
        out.append(c)
    data = json.loads(''.join(out))
    if not isinstance(data, dict): raise ValueError(f'Config must be an object: {path}')
    return data


def agent_parts(name):
    text = (ROOT / 'agents' / (name+'.md')).read_text(encoding='utf-8')
    front, body = text.split('---', 2)[1:]
    desc = next((line.split(':',1)[1].strip() for line in front.splitlines() if line.startswith('description:')), name)
    preload = [line.strip()[2:] for line in front.splitlines() if line.strip().startswith('- ')]
    return desc, body.strip(), preload


def assert_safe_destination(path):
    p = path.absolute()
    for part in [p, *p.parents]:
        if part.is_symlink(): raise ValueError(f'Refusing symlink destination: {part}')
    p = p.resolve()
    if p == ROOT or p.is_relative_to(ROOT) or ROOT.is_relative_to(p):
        raise ValueError(f'Destination overlaps bundle: {p}')


def transaction(plan, backup_root):
    """Stage every item first. Backup failures abort; never delete originals to continue."""
    staged = []; installed = []; backups = []
    try:
        for dest, payload in plan:
            assert_safe_destination(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix='.shotcraft-stage-', dir=dest.parent))
            value = stage / 'value'; staged.append(stage)
            if isinstance(payload, Path):
                if payload.is_dir(): shutil.copytree(payload, value, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                else: shutil.copy2(payload, value)
            else: value.write_text(payload, encoding='utf-8')
        for index, ((dest, _), stage) in enumerate(zip(plan, staged)):
            if dest.exists():
                backup = backup_root / str(index) / dest.name
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dest), str(backup)); backups.append((dest, backup))
            os.replace(stage / 'value', dest); installed.append(dest)
    except Exception:
        for dest in reversed(installed):
            if dest.is_dir(): shutil.rmtree(dest)
            elif dest.exists(): dest.unlink()
        for dest, backup in reversed(backups): shutil.move(str(backup), str(dest))
        raise
    finally:
        for stage in staged: shutil.rmtree(stage, ignore_errors=True)
    return [str(b) for _,b in backups]


def client_plan(client, a):
    home = Path.home()
    default = {'claude': Path(os.environ.get('CLAUDE_CONFIG_DIR', str(home/'.claude'))), 'codex': Path(os.environ.get('CODEX_HOME', str(home/'.codex'))),
               'opencode': Path(os.environ.get('XDG_CONFIG_HOME', str(home/'.config')))/'opencode'}[client]
    override = getattr(a, client+'_dir')
    base = Path(override).expanduser().absolute() if override else default.absolute()
    # Codex discovers ~/.agents/skills; keep all twelve sibling skill engines together.
    sd = Path(a.skills_dir).expanduser().absolute() if a.skills_dir else ((home/'.agents'/'skills') if client=='codex' and not override else base/'skills')
    ad = Path(a.agents_dir).expanduser().absolute() if a.agents_dir else base/'agents'
    for dest in [base, sd, ad]: assert_safe_destination(dest)
    repo = Path(a.repo).expanduser().resolve() if a.repo else sd/'video-shotcraft'
    source_repo = repo if a.repo else ROOT/'local-upstream'/'video-shotcraft'
    for required in ['SKILL.md', 'references/pipeline.md', 'template/package.json']:
        if not (source_repo/required).is_file(): raise ValueError(f'Incomplete upstream: {source_repo/required}')
    if a.repo and (sd.is_relative_to(repo) or repo.is_relative_to(sd)):
        raise ValueError('Skills destination must not overlap the external upstream repo')
    plan = []; owned = []
    def add(dest, value, owned_item=True):
        plan.append((dest,value))
        if owned_item: owned.append(dest)
    if not a.mcp_only:
        if not a.repo: add(repo,source_repo)
        for skill in SKILLS:
            if not (ROOT/skill/'SKILL.md').is_file(): raise ValueError(f'Missing skill {skill}')
            add(sd/skill, ROOT/skill)
        # config is written into a staged copy below, not as an overlapping transaction destination.
        for name in AGENTS:
            desc, body, preload = agent_parts(name)
            if client=='claude': add(ad/(name+'.md'), ROOT/'agents'/(name+'.md'))
            else:
                instructions = 'Read only the skills needed for this task from '+str(sd)+'.\n'
                instructions += 'Suggested starting skills: '+', '.join(preload)+'.\n'+body
                if client=='opencode':
                    add(ad/(name+'.md'), '---\ndescription: '+json.dumps(desc)+'\nmode: subagent\n---\n\n'+instructions+'\n')
                else: add(ad/(name+'.toml'), 'developer_instructions = '+json.dumps(instructions,ensure_ascii=False)+'\n')
        add(base/'shotcraft.py',ROOT/'shotcraft.py')
        add(base/'shotcraft-paths.json',json.dumps({'skills_dir':str(sd),'mcp_dir':str(base/'mcp')},indent=2)+'\n')
        add(base/'shotcraft-doctor.py',ROOT/'doctor.py')
    elif not all((sd/x/'SKILL.md').is_file() for x in SKILLS):
        raise ValueError('MCP-only requires an existing complete skill installation; run install.py first')
    add(base/'mcp',ROOT/'mcp')
    env = {'SHOTCRAFT_SKILLS_DIR':str(sd),'VIDEO_SHOTCRAFT_ROOT':str(repo), 'PYTHONUTF8':'1'}
    servers = {name:{'command':sys.executable,'args':[str(base/path)],'env':env} for name,path in MCP_SERVERS.items()}
    # Avoid registering the same director twice (legacy alias was doubling tools/context).
    cfg = None
    if not a.skip_mcp:
        if client=='claude':
            cfg = base.parent/'.claude.json' if base.name=='.claude' else base/'.claude.json'
            data = read_json_config(cfg); bucket = data.setdefault('mcpServers',{})
            if not isinstance(bucket,dict): raise ValueError('mcpServers must be an object')
            conflicts=set(bucket)&set(servers)
            if conflicts and not a.upgrade: raise ValueError('Existing Shotcraft MCP config; use --upgrade')
            bucket.update(servers)
            if a.upgrade and bucket.get('shotcraft-pro',{}).get('args',[])==servers['shotcraft-director']['args']:
                bucket.pop('shotcraft-pro')
            add(cfg,json.dumps(data,indent=2,ensure_ascii=False)+'\n',False)
        elif client=='opencode':
            cfg = base/'opencode.jsonc' if (base/'opencode.jsonc').exists() else base/'opencode.json'
            if (base/'opencode.jsonc').exists() and (base/'opencode.json').exists():
                raise ValueError('Both opencode.json and opencode.jsonc exist; consolidate them before installing')
            data=read_json_config(cfg);bucket=data.setdefault('mcp',{})
            if not isinstance(bucket,dict): raise ValueError('mcp must be an object')
            if set(bucket)&set(servers) and not a.upgrade: raise ValueError('Existing Shotcraft MCP config; use --upgrade')
            for name,server in servers.items():
                bucket[name]={'type':'local','command':[server['command'],*server['args']], 'environment':env,'enabled':True,'timeout':900000}
            add(cfg,json.dumps(data,indent=2,ensure_ascii=False)+'\n',False)
        else:
            cfg=base/'config.toml';old=cfg.read_text(encoding='utf-8') if cfg.exists() else ''
            tomllib.loads(old) # A corrupt existing configuration must never be discarded.
            if BEGIN in old or END in old:
                if not a.upgrade: raise ValueError('Existing Shotcraft config; use --upgrade')
                if old.count(BEGIN)!=1 or old.count(END)!=1 or old.index(BEGIN)>old.index(END): raise ValueError('Invalid managed config markers')
                old=old[:old.index(BEGIN)]+old[old.index(END)+len(END):]
            parsed=tomllib.loads(old)
            if set(parsed.get('mcp_servers',{}))&set(servers): raise ValueError('Unmanaged Shotcraft MCP tables exist; migrate them before install')
            block=['',BEGIN]
            for name,server in servers.items():
                block += [f'[mcp_servers.{json.dumps(name)}]', 'command = '+json.dumps(server['command']),
                          'args = '+json.dumps(server['args']), 'tool_timeout_sec = 900',
                          f'[mcp_servers.{json.dumps(name)}.env]', *[k+' = '+json.dumps(v) for k,v in env.items()], '']
            if not a.mcp_only or all((ad/(name+".toml")).is_file() for name in AGENTS):
                for name in AGENTS:
                    role=name.replace('-','_')
                    if role in parsed.get('agents',{}): raise ValueError(f'Unmanaged Codex agent exists: {role}')
                    desc,_,_=agent_parts(name)
                    block += [f'[agents.{role}]','description = '+json.dumps(desc),'config_file = '+json.dumps(str(ad/(name+'.toml'))),'']
            block.append(END)
            text=old.rstrip()+'\n'+'\n'.join(block)+'\n';tomllib.loads(text);add(cfg,text,False)
    for dest,_ in plan: assert_safe_destination(dest)
    if not a.upgrade:
        existing=[str(x) for x in owned if x.exists()]
        if existing: raise ValueError('Existing install; use --upgrade to back up and replace: '+existing[0])
    return base,sd,repo,plan,cfg


def main():
    p=argparse.ArgumentParser(description='Install Shotcraft skills, native agents and MCP for local coding clients')
    p.add_argument('--client',choices=['claude','codex','opencode','all'],default='claude')
    for client in ['claude','codex','opencode']: p.add_argument('--'+client+'-dir')
    p.add_argument('--repo');p.add_argument('--skills-dir');p.add_argument('--agents-dir')
    p.add_argument('--upgrade',action='store_true');p.add_argument('--skip-mcp',action='store_true')
    p.add_argument('--mcp-only',action='store_true')
    p.add_argument('--no-pip',action='store_true',help='Legacy flag; dependency installation is opt-in now')
    p.add_argument('--install-deps',action='store_true',help='Install requirements into the selected Python interpreter; use a venv')
    p.add_argument('--with-coqui',action='store_true',help='Explicit opt-in to installing optional coqui-tts')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    if a.client=='all' and (a.skills_dir or a.agents_dir):p.error('Directory overrides require one --client')
    try:
        clients=['claude','codex','opencode'] if a.client=='all' else [a.client]
        plans=[client_plan(c,a) for c in clients] # Preflight ALL targets before mutation.
        all_dest=[d for _,_,_,plan,_ in plans for d,_ in plan]
        if len(set(all_dest))!=len(all_dest):raise ValueError('Client destination paths overlap')
        for i,d in enumerate(all_dest):
            if any(d in other.parents or other in d.parents for other in all_dest[i+1:]): raise ValueError('Nested installation destinations')
        if a.dry_run:
            print(json.dumps({'version':BUNDLE_VERSION,'clients':clients,'destinations':list(map(str,all_dest))},indent=2));return
        if a.install_deps or a.with_coqui:
            cmd=[sys.executable,'-m','pip','install','-r',str(ROOT/'requirements.txt')]
            if a.with_coqui:cmd.append('coqui-tts')
            subprocess.run(cmd,check=True)
        with tempfile.TemporaryDirectory(prefix='shotcraft-config-') as td:
            full=[]
            for i,(base,sd,repo,plan,cfg) in enumerate(plans):
                if not a.mcp_only:
                    staged=Path(td)/str(i);shutil.copytree(ROOT/'shotcraft-local',staged)
                    (staged/'config.json').write_text(json.dumps({'repo_path':str(repo),'python_bin':sys.executable,'bundle_version':BUNDLE_VERSION,'skills_dir':str(sd),'mcp_dir':str(base/'mcp')},indent=2),encoding='utf-8')
                    plan=[(d,staged if d==sd/'shotcraft-local' else value) for d,value in plan]
                full.extend(plan)
            stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            backups=transaction(full,plans[0][0]/'.shotcraft-backups'/stamp)
        print(json.dumps({'ok':True,'version':BUNDLE_VERSION,'clients':clients,'backups':backups,'mcp_servers_per_client':0 if a.skip_mcp else len(MCP_SERVERS),'note':'Restart the client. Run shotcraft-doctor.py. TTS models and Node dependencies are separate.'},indent=2))
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:p.exit(2,f'Installation stopped: {exc}\n')

if __name__=='__main__': main()
