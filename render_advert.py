"""
HumanitAI — Hyperframes advert renderer (pure stdlib, piped to ffmpeg).
14s, 1920x1080, 30fps, 420 frames. Five visual beats, no baked text
(captions are synced HTML overlay in the site section).

BEATS (single source of truth, seconds):
  noise    0.0 - 2.0   teal particles scatter chaotically
  settle   2.0 - 5.0   teal particles lerp into a UK-city lattice
  lock     5.0 - 7.5   amber Middlesbrough node blooms + locks
  deploy   7.5 -10.5   amber CHW rings converge onto Middlesbrough
  measure 10.5 -14.0   severity bars draw in; teal settles to steady grid
"""
import math, os, subprocess, random

W, H = 1920, 1080
FPS = 30
FRAMES = int(14 * FPS)            # 420
out = "/opt/data/wordhumanitai_v2/advert.mp4"

TEAL   = (16, 214, 189)          # 0x10D6BD
TEAL_D = (11, 168, 148)          # deeper teal
AMBER  = (224, 122, 10)         # E07A0A
AMBER_B= (255, 178, 46)         # bright amber
WHITE  = (244, 242, 235)
INK    = (8, 9, 12)              # near-black bg

# 18 UK places (lat, lng) — same set as the live dashboard
CITIES = [
    [55.86,-4.25],[53.82,-3.05],[51.51,-0.03],[51.53,0.03],[53.41,-2.99],
    [53.48,-2.24],[54.57,-1.23],[53.79,-1.75],[53.49,-2.29],[52.95,-1.15],
    [54.97,-1.61],[53.40,-2.99],[53.74,-0.33],[53.38,-1.47],[52.63,-1.13],
    [51.45,-2.59],[51.88,-0.42],[53.80,-1.55],
]
MB_IDX = 6  # Middlesbrough

def uk_proj(lat, lng):
    x = W * 0.5 + (lng - (-3.0)) * 72.0
    y = H * 0.5 - (lat - 54.5) * 72.0
    return x, y

def ease(t):
    t = min(1.0, max(0.0, t))
    return 2 * t * t if t < 0.5 else 1 - ((-2 * t + 2) ** 2) / 2
def ramp(t, t0, t1):
    return ease(min(1.0, max(0.0, (t - t0) / (t1 - t0))))

def lerp(a, b, t):
    return a + (b - a) * t

def blend(buf, x, y, col, a):
    x = int(x); y = int(y)
    if not (0 <= x < W and 0 <= y < H) or a <= 0:
        return
    idx = (y * W + x) * 3
    buf[idx]   = int(buf[idx]   * (1 - a) + col[0] * a)
    buf[idx+1] = int(buf[idx+1] * (1 - a) + col[1] * a)
    buf[idx+2] = int(buf[idx+2] * (1 - a) + col[2] * a)

def draw_disc(buf, cx, cy, r, col, a):
    cx, cy = int(round(cx)), int(round(cy))
    r = max(1, int(round(r)))
    for y in range(max(0, cy - r), min(H, cy + r)):
        for x in range(max(0, cx - r), min(W, cx + r)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                blend(buf, x, y, col, a)

def draw_ring(buf, cx, cy, r, thick, col, a):
    cx, cy = int(round(cx)), int(round(cy))
    r = int(round(r)); rin = max(0, r - int(thick))
    for y in range(max(0, cy - r - 1), min(H, cy + r + 2)):
        for x in range(max(0, cx - r - 1), min(W, cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if rin <= d <= r:
                blend(buf, x, y, col, a * min(1.0, r - d + 0.5))

def draw_line(buf, x0, y0, x1, y1, col, a):
    x0, y0, x1, y1 = [int(round(v)) for v in (x0, y0, x1, y1)]
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        t = i / n
        blend(buf, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, col, a)

def draw_rect(buf, x0, y0, w, h, col, a):
    for y in range(max(0, int(y0)), min(H, int(y0 + h))):
        for x in range(max(0, int(x0)), min(W, int(x0 + w))):
            blend(buf, x, y, col, a)

# ---- precompute city screen positions ----
CXY = [uk_proj(c[0], c[1]) for c in CITIES]
MBX, MBY = CXY[MB_IDX]

# ---- particles ----
rnd = random.Random(7)
N = 620
parts = []
for i in range(N):
    nx = rnd.uniform(0, W)
    ny = rnd.uniform(0, H)
    ci = rnd.randrange(len(CITIES))
    tx = CXY[ci][0] + rnd.uniform(-34, 34)
    ty = CXY[ci][1] + rnd.uniform(-34, 34)
    # phase offset for steady-grid convergence in measure beat
    gx = W * 0.5 + ((i % 31) - 15) * 30.0
    gy = H * 0.42 + ((i // 31) - 10) * 26.0
    parts.append([nx, ny, tx, ty, gx, gy])
    parts[-1].append(rnd.uniform(0, 6.28))  # jitter phase

# CHW deploy rings: scattered start positions -> converge to Middlesbrough
M = 16
chw = []
for i in range(M):
    sx = rnd.uniform(W * 0.2, W * 0.8)
    sy = rnd.uniform(H * 0.15, H * 0.85)
    chw.append([sx, sy])

bg_pixel = bytes([INK[0], INK[1], INK[2]])
def fill_bg(buf):
    for i in range(0, len(buf), 3):
        buf[i] = bg_pixel[0]; buf[i+1] = bg_pixel[1]; buf[i+2] = bg_pixel[2]

cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
       "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
       "-movflags", "+faststart", out]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for fr in range(FRAMES):
    t = fr / FPS
    buf = bytearray(W * H * 3)
    fill_bg(buf)

    noise  = ramp(t, 0.0, 2.0)
    settle = ramp(t, 2.0, 5.0)
    lock   = ramp(t, 5.0, 7.5)
    deploy = ramp(t, 7.5, 10.5)
    meas   = ramp(t, 10.5, 14.0)

    # ---- faint city lattice (always faintly present once settled) ----
    if settle > 0:
        for (cx, cy) in CXY:
            draw_disc(buf, cx, cy, 2.2, TEAL_D, 0.18 * settle)
        for a in range(len(CXY)):
            for b in range(a + 1, len(CXY)):
                if (CXY[a][0]-CXY[b][0])**2 + (CXY[a][1]-CXY[b][1])**2 < 19000:
                    draw_line(buf, CXY[a][0], CXY[a][1], CXY[b][0], CXY[b][1],
                              TEAL_D, 0.05 * settle)

    # ---- main particles ----
    for p in parts:
        nx, ny, tx, ty, gx, gy, ph = p
        # noise drift
        jx = math.sin(t * 5 + ph) * 26 + math.cos(t * 3.1 + ph) * 14
        jy = math.cos(t * 4 + ph) * 26 + math.sin(t * 2.7 + ph) * 14
        if t < 2.0:
            x = nx + jx * noise; y = ny + jy * noise
            col = TEAL; a = 0.35 + 0.25 * noise
            draw_disc(buf, x, y, 2.0 + 1.2 * noise, col, a)
        else:
            # settle -> target
            x = lerp(nx + jx, tx, settle)
            y = lerp(ny + jy, ty, settle)
            if meas > 0:                       # re-form into steady grid
                x = lerp(x, gx, meas * 0.85)
                y = lerp(y, gy, meas * 0.85)
            col = TEAL if meas < 0.5 else WHITE
            a = 0.5 * (1 - 0.3 * meas) + 0.15
            draw_disc(buf, x, y, 2.4, col, a)

    # ---- lock: amber Middlesbrough bloom ----
    if lock > 0 or deploy > 0 or meas > 0:
        pulse = 0.5 + 0.5 * math.sin(t * 3)
        draw_disc(buf, MBX, MBY, 10 + 8 * lock, AMBER, 0.55 * max(lock, deploy))
        draw_ring(buf, MBX, MBY, 16 + 10 * lock + 6 * pulse, 2, AMBER_B, 0.5 * max(lock, 0.3))

    # ---- deploy: CHW rings converge onto Middlesbrough ----
    if deploy > 0:
        for i, (sx, sy) in enumerate(chw):
            x = lerp(sx, MBX, deploy)
            y = lerp(sy, MBY, deploy)
            # slight spiral arrival
            ang = i * 0.4
            x += math.cos(ang + t * 4) * (1 - deploy) * 40
            y += math.sin(ang + t * 4) * (1 - deploy) * 40
            draw_ring(buf, x, y, 7, 2.5, AMBER_B, 0.6 * deploy)
        # community cluster forming around the node
        for k in range(10):
            ca = k * 0.63
            cxp = MBX + math.cos(ca) * 26 * deploy
            cyp = MBY + math.sin(ca) * 26 * deploy
            draw_disc(buf, cxp, cyp, 2.6, TEAL, 0.5 * deploy)

    # ---- measure: severity bars + SROI mini-viz along the bottom ----
    if meas > 0:
        bx = W * 0.5 - 360
        by = H - 150
        labels = [("Poverty", 0.86, AMBER), ("Homeless", 0.62, AMBER),
                  ("NHS waits", 0.74, TEAL_D), ("NEET", 0.58, TEAL_D),
                  ("Confidence", 0.81, TEAL)]
        for i, (lab, frac, col) in enumerate(labels):
            yy = by + i * 22
            draw_rect(buf, bx, yy, 720, 13, (22, 24, 28), 0.7)
            fw = 720 * frac * meas
            draw_rect(buf, bx, yy, fw, 13, col, 0.9)
            # tick at end
            draw_disc(buf, bx + fw, yy + 6, 3, WHITE, 0.8 * meas)
        # SROI ribbon
        sr = ramp(t, 11.5, 13.5)
        draw_rect(buf, bx, by - 40, 720 * sr, 6, TEAL, 0.9)

    try:
        proc.stdin.write(bytes(buf))
    except BrokenPipeError:
        break
    if fr % 60 == 0:
        print("frame", fr, "t=%.1f" % t, flush=True)

proc.stdin.close()
proc.wait()
print("DONE", FRAMES, "->", out, "exit", proc.returncode)
