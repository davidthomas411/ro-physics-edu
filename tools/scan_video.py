"""Find the page-down events in a screen recording of the e-book and the still intervals between them.
Usage: python tools/scan_video.py video.mp4 [--top 60]
A page-down shows up as a burst of frame-to-frame change; the page is still in between."""
import sys, cv2, numpy as np

def motion_signal(path, top=60):
    cap = cv2.VideoCapture(str(path)); fps = cap.get(cv2.CAP_PROP_FPS) or 60.0
    sig = []; prev = None
    while True:
        ok, fr = cap.read()
        if not ok: break
        g = cv2.cvtColor(fr[top:, :], cv2.COLOR_BGR2GRAY)
        g = cv2.resize(g, (480, 215), interpolation=cv2.INTER_AREA).astype(np.float32)
        sig.append(0.0 if prev is None else float(np.abs(g - prev).mean()))
        prev = g
    cap.release()
    return np.array(sig), fps

def still_runs(sig, fps, eps=0.25, min_frames=4):
    """Runs of consecutive frames whose change is below eps. Returns [(first_frame, last_frame)]."""
    runs, start = [], None
    for i, m in enumerate(sig):
        if m < eps:
            if start is None: start = i
        else:
            if start is not None and i - start >= min_frames: runs.append((start, i - 1))
            start = None
    if start is not None and len(sig) - start >= min_frames: runs.append((start, len(sig) - 1))
    return runs

if __name__ == "__main__":
    sig, fps = motion_signal(sys.argv[1])
    print(f"{len(sig)} frames at {fps:.1f} fps = {len(sig)/fps:.1f} s")
    print("change per frame: percentiles 10/50/90/99 =", [round(float(np.percentile(sig, p)), 3) for p in (10, 50, 90, 99)])
    for eps in (0.05, 0.1, 0.25, 0.5, 1.0):
        r = still_runs(sig, fps, eps)
        d = [(b - a + 1) / fps for a, b in r]
        print(f"eps {eps:>4}: {len(r):3d} still runs; median length {np.median(d) if d else 0:.2f} s; shortest {min(d) if d else 0:.2f} s")
