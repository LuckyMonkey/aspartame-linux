#!/usr/bin/env python3
"""Guest regression: restore Pippy source from its Journal object."""
import os, subprocess, sys, time
from pathlib import Path
BUNDLE_ID="org.laptop.Pippy"; MARKER="pippyactivity4.PippyActivity"
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
        if depth>12:return None
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
        if depth>12:return None
        if node.get_process_id()==pid and node.get_name()==name:return node
        for i in range(node.get_child_count()):
            child=node.get_child_at_index(i)
            if child is not None:
                got=find_named(child,pid,name,depth+1)
                if got is not None:return got
        return None
    def launch(uid="",expected="Pippy"):
        assert journal.LaunchBundle(BUNDLE_ID,uid);pid,aid=wait_for("Pippy process",lambda:next(iter(procs()),None));wait_for("service",lambda:bus.name_has_owner("org.laptop.Activity"+aid));wait_for("shell",lambda:shell.ActivateActivity(aid));return pid,aid,wait_for("visible Pippy",lambda:find(Atspi.get_desktop(0),pid,expected))
    def stop(pid,aid):
        assert shell.StopActivity(aid);wait_for("exit",lambda:not Path(f"/proc/{pid}").exists());assert not bus.name_has_owner("org.laptop.Activity"+aid);assert not shell.ActivateActivity(aid)
    if procs():raise SystemExit("Pippy already running")
    cycles=int(sys.argv[1]) if len(sys.argv)>1 else 2
    for cycle in range(1,cycles+1):
        pid,aid,node=launch();stop(pid,aid);rows,_=store.find(dbus.Dictionary({"activity_id":aid},signature="sv"),dbus.Array(["uid"],signature="s"));assert len(rows)==1
        uid=str(rows[0]["uid"]);fn=Path(str(store.get_filename(uid)));fn.write_text('print("Aspartame")\n',encoding="utf-8");rpid,raid,rnode=launch(uid,"Aspartame");assert "Aspartame" in Atspi.Text.get_text(rnode,0,-1)
        run=wait_for("Run action",lambda:find_named(Atspi.get_desktop(0),rpid,"Run"));assert run and run.get_n_actions();assert run.get_action().do_action(0)
        wait_for("runner completion",lambda:find(Atspi.get_desktop(0),rpid,"Finished"))
        output=wait_for("program output",lambda:find_named(Atspi.get_desktop(0),rpid,"Program output"));assert "Aspartame" in Atspi.Text.get_text(output,0,-1)
        if len(sys.argv) > 2 and cycle == cycles:
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "x11grab", "-video_size", "1920x1080", "-i", ":0", "-frames:v", "1", "-y", sys.argv[2]], check=True)
        stop(rpid,raid);assert "Aspartame" in fn.read_text(encoding="utf-8")
        print(f"cycle={cycle} pid={pid} resumed_pid={rpid} object={uid} resume=PASS service-release=PASS shell-cleanup=PASS",flush=True)
    print("pippy-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded",flush=True)
if __name__=="__main__":main()
