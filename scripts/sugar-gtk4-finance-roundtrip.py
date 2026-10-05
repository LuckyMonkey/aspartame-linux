#!/usr/bin/env python3
"""Guest regression: restore Finance transactions from its Journal object."""
import json, os, subprocess, sys, time
from pathlib import Path
BUNDLE_ID="org.laptop.community.Finance"; MARKER="financeactivity4.FinanceActivity"
def wait_for(desc,fn):
    end=time.monotonic()+15
    while time.monotonic()<end:
        v=fn()
        if v:return v
        time.sleep(.1)
    raise RuntimeError(f"Timed out: {desc}")
def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():raise SystemExit("Run inside Aspartame guest")
    if os.getuid()==0:
        shells=subprocess.check_output(["pgrep","-u","aspartame","-f","/sources/sugar/src/jarabe/main.py"],text=True).splitlines()
        if len(shells)!=1:raise SystemExit("Expected one modern shell")
        env=dict(x.split("=",1) for x in Path(f"/proc/{shells[0]}/environ").read_bytes().decode().split("\0") if "=" in x);py=os.environ.get("GTK4_PYTHON") or next((candidate for candidate in ("/usr/lib/aspartame/gtk4-preview/venv/bin/python", "/home/aspartame/Development/gtk4-preview/venv/bin/python") if Path(candidate).exists()), sys.executable);os.setgroups([]);os.setgid(1000);os.setuid(1000);os.execve(py,[py,__file__,*sys.argv[1:]],env)
    import dbus,gi
    gi.require_version("Atspi","2.0");from gi.repository import Atspi
    bus=dbus.SessionBus();journal=dbus.Interface(bus.get_object("org.laptop.Journal","/org/laptop/Journal"),"org.laptop.Journal");shell=dbus.Interface(bus.get_object("org.laptop.Shell","/org/laptop/Shell"),"org.laptop.Shell");store=dbus.Interface(bus.get_object("org.laptop.sugar.DataStore","/org/laptop/sugar/DataStore"),"org.laptop.sugar.DataStore")
    def procs():
        out=[]
        for p in Path("/proc").glob("[0-9]*/cmdline"):
            try:a=p.read_bytes().decode().split("\0")
            except (FileNotFoundError,PermissionError,ProcessLookupError):continue
            if MARKER in a:out.append((int(p.parent.name),a[a.index("--activity-id")+1]))
        return out
    def find(node,pid,text,depth=0):
        if depth>24:return None
        if node.get_process_id()==pid:
            try:v=Atspi.Text.get_text(node,0,-1)
            except Exception:v=""
            if text in v:return node
        for i in range(node.get_child_count()):
            c=node.get_child_at_index(i)
            if c is not None:
                got=find(c,pid,text,depth+1)
                if got is not None:return got
        return None
    def find_named(node,pid,name,depth=0):
        if depth>24:return []
        matches=[]
        if node.get_process_id()==pid:
            label=node.get_name() or ""
            try: label += " " + Atspi.Text.get_text(node,0,-1)
            except Exception: pass
            if name in label and node.get_role_name() == "button":matches.append(node)
        for i in range(node.get_child_count()):
            child=node.get_child_at_index(i)
            if child is not None:matches.extend(find_named(child,pid,name,depth+1))
        return matches
    def launch(uid="",expected="Finance"):
        assert journal.LaunchBundle(BUNDLE_ID,uid);pid,aid=wait_for("Finance process",lambda:next(iter(procs()),None));wait_for("service",lambda:bus.name_has_owner("org.laptop.Activity"+aid));wait_for("shell",lambda:shell.ActivateActivity(aid));return pid,aid,wait_for("visible Finance",lambda:find(Atspi.get_desktop(0),pid,expected))
    def stop(pid,aid):
        assert shell.StopActivity(aid);wait_for("exit",lambda:not Path(f"/proc/{pid}").exists());assert not bus.name_has_owner("org.laptop.Activity"+aid);assert not shell.ActivateActivity(aid)
    if procs():raise SystemExit("Finance already running")
    cycles=int(sys.argv[1]) if len(sys.argv)>1 else 2
    for cycle in range(1,cycles+1):
        pid,aid,node=launch();stop(pid,aid);rows,_=store.find(dbus.Dictionary({"activity_id":aid},signature="sv"),dbus.Array(["uid"],signature="s"));assert len(rows)==1
        uid=str(rows[0]["uid"]);fn=Path(str(store.get_filename(uid)));fn.write_text('{"transactions":[{"value":125.5,"description":"Grant"},{"value":-25.5,"description":"Supplies"}]}\n',encoding="utf-8");rpid,raid,rnode=launch(uid,"Balance: 100.00");assert "Balance: 100.00" in Atspi.Text.get_text(rnode,0,-1)
        remove=wait_for("Supplies removal action",lambda:find_named(Atspi.get_desktop(0),rpid,"Remove Supplies"));assert remove;assert remove[-1].get_action().do_action(0)
        wait_for("removed transaction balance",lambda:find(Atspi.get_desktop(0),rpid,"Balance: 125.50"))
        if len(sys.argv)>2 and cycle==cycles:
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-f","x11grab","-video_size","1920x1080","-i",":0","-frames:v","1","-y",sys.argv[2]],check=True)
        stop(rpid,raid)
        def saved_transactions():
            try: payload=json.loads(Path(str(store.get_filename(uid))).read_text(encoding="utf-8"))
            except (OSError,UnicodeError,ValueError,TypeError,json.JSONDecodeError): return None
            transactions=payload.get("transactions") if isinstance(payload,dict) else None
            return transactions if isinstance(transactions,list) and len(transactions)==1 else None
        saved=wait_for("saved transaction removal",saved_transactions);assert saved[0]["description"]=="Grant"
        print(f"cycle={cycle} pid={pid} resumed_pid={rpid} object={uid} resume=PASS service-release=PASS shell-cleanup=PASS",flush=True)
    print("finance-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded",flush=True)
if __name__=="__main__":main()
