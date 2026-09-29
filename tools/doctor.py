"""Environment doctor: reports Python, Godot executable/version, display availability. Installs nothing."""
import argparse, os, platform, shutil, subprocess, sys

PINNED = "4.7.2.stable"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--godot", default=os.environ.get("GODOT_BIN"))
    a = ap.parse_args()
    ok = True
    print("python:", sys.version.split()[0], "OK" if sys.version_info >= (3, 10) else "TOO OLD")
    print("platform:", platform.platform())
    g = a.godot or shutil.which("godot") or shutil.which("godot4")
    if not g or not os.path.exists(g):
        print("godot: NOT FOUND (set GODOT_BIN or --godot)"); ok = False
    else:
        v = subprocess.run([g, "--version"], capture_output=True, text=True, timeout=60).stdout.strip()
        print("godot:", g, v, "OK" if v.startswith(PINNED) else f"MISMATCH (pinned {PINNED})")
        ok &= v.startswith(PINNED)
    disp = os.environ.get("DISPLAY") or (shutil.which("xvfb-run") and "xvfb-run available")
    print("display:", disp or "none (headless only; screenshots need a display)")
    print("doctor:", "OK" if ok else "ISSUES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
