#!/usr/bin/env python3
"""Guest regression: restore Markdown source and preview from Journal."""
import os, subprocess, sys, time
from pathlib import Path
BUNDLE_ID="org.sugarlabs.Markdown"; MARKER="markdownactivity4.MarkdownActivity"
def wait_for(desc, fn):
    end=time.monotonic()+15
    while time.monotonic()<end:
        value=fn()
        if value:return value
        time.sleep(.1)
    raise RuntimeError(f"Timed out: {desc}")
def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():raise SystemExit("Run inside Aspartame guest")
    if os.getuid()==0:
        shells=subprocess.check_output(["pgrep","-u","aspartame","-f","/sources/sugar/src/jarabe/main.py"],text=True).splitlines()
        if len(shells)!=1:raise SystemExit("Expected one modern shell")
        env=dict(x.split("=",1) for x in Path(f"/proc/{shells[0]}/environ").read_bytes().decode().split("\0") if "=" in x)
        py="/home/aspartame/Development/gtk4-preview/venv/bin/python";os.setgroups([]);os.setgid(1000);os.setuid(1000);os.execve(py,[py,__file__,*sys.argv[1:]],env)
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
            try:visible=Atspi.Text.get_text(node,0,-1)
            except Exception:visible=""
            if text in visible:return node
        for i in range(node.get_child_count()):
            c=node.get_child_at_index(i)
            if c is not None:
                got=find(c,pid,text,depth+1)
                if got is not None:return got
        return None
    def launch(uid="",expected="Markdown"):
        assert journal.LaunchBundle(BUNDLE_ID,uid);pid,aid=wait_for("Markdown process",lambda:next(iter(procs()),None));wait_for("service",lambda:bus.name_has_owner("org.laptop.Activity"+aid));wait_for("shell",lambda:shell.ActivateActivity(aid));return pid,aid,wait_for("visible Markdown",lambda:find(Atspi.get_desktop(0),pid,expected))
    def stop(pid,aid):
        assert shell.StopActivity(aid);wait_for("exit",lambda:not Path(f"/proc/{pid}").exists());assert not bus.name_has_owner("org.laptop.Activity"+aid);assert not shell.ActivateActivity(aid)
    if procs():raise SystemExit("Markdown already running")
    cycles=int(sys.argv[1]) if len(sys.argv)>1 else 2
    for cycle in range(1,cycles+1):
        pid,aid,node=launch();stop(pid,aid);rows,_=store.find(dbus.Dictionary({"activity_id":aid},signature="sv"),dbus.Array(["uid"],signature="s"));assert len(rows)==1
        uid=str(rows[0]["uid"]);fn=Path(str(store.get_filename(uid)));fn.write_text("# GTK4\n\nSugar stays focused.\n",encoding="utf-8");rpid,raid,rnode=launch(uid,"GTK4");assert "GTK4" in Atspi.Text.get_text(rnode,0,-1);stop(rpid,raid);assert "GTK4" in fn.read_text(encoding="utf-8")
        print(f"cycle={cycle} pid={pid} resumed_pid={rpid} object={uid} resume=PASS service-release=PASS shell-cleanup=PASS",flush=True)
    print("markdown-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded",flush=True)
if __name__=="__main__":main()
