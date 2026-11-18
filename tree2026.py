"""Rotating 3D Christmas tree in its own window (Tkinter).
Python standard library only: no pip install needed (tkinter ships with Python on Windows).

    python christmas_tree_window.py

Mouse drag = rotate | wheel = zoom | Space = pause | Left/Right = spin speed
F or F11 = fullscreen | R = restart the growing animation | Esc = leave fullscreen / quit
"""
import math
import random
import time

# ---- tweak me ---------------------------------------------------------------
RES = 280          # internal render resolution (square). Bigger = sharper but slower.
QUALITY = 1.0      # point-count multiplier. Lower (0.6) if it is choppy, higher (1.5) for a denser tree.
SPIN = 2 * math.pi / 20   # one turn every 20 s
MESSAGE = "M E R R Y   C H R I S T M A S   2 0 2 6"
# -----------------------------------------------------------------------------

GROUND, Y0, Y1, RMAX = -0.98, -0.80, 0.86, 0.58
CAM, TILT = 4.0, 0.22
NEEDLE, SNOW, TRUNK, GARLAND, GIFT, RIBBON, FLOOR, STAR = range(8)

RED, GOLD, SILVER = (242, 31, 26), (255, 194, 56), (219, 224, 242)
BLUE, GREEN, WARM, WHITE = (38, 97, 255), (26, 184, 64), (255, 214, 140), (255, 255, 255)
BARK = (115, 69, 31)

T_GROW, T_GARLAND, T_BALLS = (0.4, 6.5), (6.5, 8.8), (8.0, 10.5)
T_LIGHTS, T_GIFTS, T_STAR, T_MSG = (9.0, 11.5), (10.0, 12.0), 12.0, 13.0

_l = math.sqrt(0.5 ** 2 + 0.6 ** 2 + 0.65 ** 2)
LX, LY, LZ = -0.5 / _l, 0.6 / _l, -0.65 / _l


def clamp(x, a, b):
    return a if x < a else b if x > b else x


def popf(x):                       # ease-out-back: 0 -> overshoot -> 1
    x = clamp(x, 0, 1) - 1
    return 1 + 2.7 * x ** 3 + 1.7 * x ** 2


def envelope(y):
    return RMAX * (1 - clamp((y - Y0) / (Y1 - Y0), 0, 1)) ** 1.05


def grow_time(y):
    return T_GROW[0] + (T_GROW[1] - T_GROW[0]) * clamp((y - GROUND) / (Y1 - GROUND), 0, 1)


# ------------------------------------------------------------------ scene
def build():
    random.seed(7)
    rnd, gauss, uni = random.random, random.gauss, random.uniform
    Q = QUALITY
    pts, tips = [], []

    def add(x, y, z, nx, ny, nz, k, col, t0, gain=1.0, ph=0.0):
        l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        pts.append((x, y, z, nx / l, ny / l, nz / l, k, col[0], col[1], col[2], t0, gain, ph))

    # needles: whorls of drooping branches
    for i in range(18):
        y = Y0 + 0.02 + (Y1 - 0.06 - Y0 - 0.02) * i / 17
        u = (y - Y0) / (Y1 - Y0)
        R = envelope(y) + 0.05
        nb = int(5 + 9 * (1 - u))
        for b in range(nb):
            a = 2 * math.pi * (b + 0.5 * rnd()) / nb + i * 0.77
            L = R * uni(0.85, 1.08)
            dx, dz = math.cos(a), math.sin(a)
            sx, sz = -dz, dx
            for _ in range(int((30 + 190 * L) * Q)):
                s = rnd() ** 0.65
                spread = (0.025 + 0.09 * s) * gauss(0, 1)
                sl = s * L
                px, pz = dx * sl + sx * spread, dz * sl + sz * spread
                py = y + 0.06 * sl - 0.20 * sl * sl + 0.012 * gauss(0, 1)
                nx, ny, nz = dx * 0.75 + 0.3 * gauss(0, 1), 0.55 + 0.3 * gauss(0, 1), dz * 0.75 + 0.3 * gauss(0, 1)
                ao = (0.55 + 0.45 * s ** 1.3) * uni(0.75, 1.1)
                snow = s > 0.5 and rnd() < 0.06 * s and ny > 0.2
                g = rnd()
                col = WHITE if snow else (255 * (0.10 + 0.12 * g), 255 * (0.55 + 0.40 * g), 255 * (0.18 + 0.14 * g))
                add(px, py, pz, nx, ny, nz, SNOW if snow else NEEDLE, col, grow_time(py), 1.0 if snow else ao)
            tl = 0.93 * L
            tips.append((dx * tl, y + 0.06 * tl - 0.20 * tl * tl, dz * tl))

    # dark inner cone so nothing shows through the branches
    for _ in range(int(2500 * Q)):
        y = Y0 + (Y1 - 0.1 - Y0) * rnd()
        phi, r = rnd() * 2 * math.pi, 0.8 * envelope(y)
        add(math.cos(phi) * r, y, math.sin(phi) * r, math.cos(phi), 0.3, math.sin(phi), NEEDLE, (31, 140, 51), grow_time(y), 0.8)
    # trunk
    for _ in range(150):
        y, phi = GROUND + rnd() * (Y0 + 0.1 - GROUND), rnd() * 2 * math.pi
        add(math.cos(phi) * 0.075, y, math.sin(phi) * 0.075, math.cos(phi), 0, math.sin(phi), TRUNK, BARK, grow_time(y))
    # snowy floor
    for _ in range(int(450 * Q)):
        r, phi = 1.0 * math.sqrt(rnd()), rnd() * 2 * math.pi
        add(math.cos(phi) * r, GROUND, math.sin(phi) * r, 0, 1, 0, FLOOR, (107, 115, 148), 0.0, 0.45)
    # tinsel garland
    NG = int(750 * Q)
    for i in range(NG):
        u = i / (NG - 1)
        yg, ag = Y0 + 0.15 + (Y1 - Y0 - 0.45) * u, 2 * math.pi * 3.6 * u + 0.9
        swag, rg = -0.07 * abs(math.sin(ag * 2.5)), envelope(yg) + 0.07
        add(math.cos(ag) * rg + 0.016 * gauss(0, 1), yg + swag + 0.016 * gauss(0, 1), math.sin(ag) * rg + 0.016 * gauss(0, 1),
            math.cos(ag), 0.3, math.sin(ag), GARLAND, GOLD, T_GARLAND[0] + u * (T_GARLAND[1] - T_GARLAND[0]), 1.0, rnd() * 6.28)

    # presents
    gifts = [(0.3, 0.66, 0.24, 0.28, 0.24, 0.4, RED, GOLD), (1.5, 0.62, 0.18, 0.20, 0.18, 0.9, BLUE, GOLD),
             (2.6, 0.68, 0.30, 0.22, 0.26, 0.1, GOLD, RED), (3.7, 0.64, 0.20, 0.30, 0.20, 0.6, GREEN, RED),
             (4.7, 0.60, 0.26, 0.18, 0.30, 0.3, SILVER, RED), (5.6, 0.70, 0.22, 0.24, 0.22, 1.1, RED, SILVER)]
    for g, (ang, dist, w, h, d, rot, body, rib) in enumerate(gifts):
        areas = [w * d, w * d, h * d, h * d, w * h, w * h]
        tot = sum(areas)
        cr, sr = math.cos(rot), math.sin(rot)
        bx, bz = math.cos(ang) * dist, math.sin(ang) * dist
        t0 = T_GIFTS[0] + g * (T_GIFTS[1] - T_GIFTS[0]) / len(gifts)

        def put(p, n, ribbon):
            add(cr * p[0] - sr * p[2] + bx, p[1] + GROUND, sr * p[0] + cr * p[2] + bz,
                cr * n[0] - sr * n[2], n[1], sr * n[0] + cr * n[2], RIBBON if ribbon else GIFT, rib if ribbon else body, t0)

        for _ in range(int(3000 * Q * (w * h + w * d + h * d))):
            r, f = rnd() * tot, 0
            while f < 5 and r > areas[f]:
                r -= areas[f]
                f += 1
            a, b = rnd() - 0.5, rnd() - 0.5
            p, n = [((a * w, h, b * d), (0, 1, 0)), ((a * w, 0, b * d), (0, -1, 0)),
                    ((w / 2, (a + .5) * h, b * d), (1, 0, 0)), ((-w / 2, (a + .5) * h, b * d), (-1, 0, 0)),
                    ((a * w, (b + .5) * h, d / 2), (0, 0, 1)), ((a * w, (b + .5) * h, -d / 2), (0, 0, -1))][f]
            put(p, n, abs(p[0]) < 0.022 or abs(p[2]) < 0.022)
        for _ in range(40):                      # bow
            side, an = (-1 if rnd() < 0.5 else 1), 2 * math.pi * rnd()
            put((side * (0.03 + 0.03 * math.cos(an)), h + 0.03 + 0.03 * math.sin(an), 0), (math.cos(an) * side, math.sin(an), -0.4), True)

    # star on top (billboard: never yaw-rotated), filled five-pointed shape
    R, rin, P5 = 0.17, 0.17 * 0.45, 2 * math.pi / 5
    for _ in range(320):
        phi = rnd() * 2 * math.pi
        rb = rin + (R - rin) * abs((phi % P5) / P5 - 0.5) * 2
        r = rb * math.sqrt(rnd())
        add(r * math.sin(phi), Y1 + 0.12 + r * math.cos(phi), 0.0, 0, 0, -1, STAR, GOLD, T_STAR, 1.0, rnd() * 6.28)

    # baubles (drawn as shaded discs) and fairy lights (drawn as glowing plus signs)
    balls = []
    for k in range(30):
        u = (k + rnd()) / 30
        y, a = Y0 + 0.08 + u * (Y1 - Y0 - 0.38), k * 2.39996 + rnd() * 0.4
        col = RED if k % 2 == 0 else (GOLD if k % 4 == 1 else SILVER)
        balls.append((math.cos(a) * envelope(y), y - 0.03, math.sin(a) * envelope(y), 0.044 + 0.024 * (1 - u),
                      col[0], col[1], col[2], T_BALLS[0] + u * (T_BALLS[1] - T_BALLS[0]) + 0.3 * rnd()))
    random.shuffle(tips)
    others = [RED, GOLD, BLUE, GREEN, WHITE]
    lights = []
    for (x, y, z) in tips[:110]:
        col = WARM if rnd() < 0.6 else random.choice(others)
        lights.append((x, y, z, col[0], col[1], col[2], T_LIGHTS[0] + rnd() * (T_LIGHTS[1] - T_LIGHTS[0]), rnd() * 6.28))

    pts.sort(key=lambda p: p[10])
    balls.sort(key=lambda p: p[7])
    lights.sort(key=lambda p: p[6])
    stars = [(int(rnd() * RES) * RES + int(rnd() * RES), rnd() * 6.28) for _ in range(160)]
    flakes = [(rnd(), rnd(), uni(0.03, 0.09), rnd() * 6.28, rnd() < 0.3) for _ in range(110)]
    return {"pts": pts, "balls": balls, "lights": lights, "stars": stars, "flakes": flakes}


# ----------------------------------------------------------------- render
def render(sc, t, yaw, pitch, zoom):
    """Returns (PPM bytes of a RES x RES image, info dict)."""
    n = RES * RES
    R, G, B = bytearray([6]) * n, bytearray([8]) * n, bytearray([14]) * n
    depth = [1e9] * n
    c, s, ct, st = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    K, X0, YC = zoom * RES * 0.35, RES / 2.0, RES * 0.49
    sin = math.sin

    for i, ph in sc["stars"]:
        v = int(255 * (0.18 + 0.5 * sin(t * 1.3 + ph) ** 8))
        R[i], G[i], B[i] = int(v * 0.8), int(v * 0.85), v

    for x, y, z, nx, ny, nz, k, r, g, b, t0, gain, ph in sc["pts"]:
        if t0 > t:
            break
        if k == STAR:
            xr, zr = x, z
        else:
            xr, zr = x * c - z * s, x * s + z * c
        yv, zv = y * ct + zr * st, zr * ct - y * st
        f = CAM / (CAM + zv)
        ix, iy = int(X0 + xr * f * K), int(YC - yv * f * K)
        if ix < 0 or ix >= RES or iy < 0 or iy >= RES:
            continue
        i = iy * RES + ix
        if zv >= depth[i]:
            continue
        depth[i] = zv
        age = t - t0
        if k == STAR:
            fl = max(0.0, 1 - age) ** 2
            bright = 0.9 + 0.1 * sin(t * 3 + ph)
            r, g, b = r + (255 - r) * fl, g + (255 - g) * fl, b + (255 - b) * fl
        else:
            nxr, nzr = nx * c - nz * s, nx * s + nz * c
            lam = nxr * LX + (ny * ct + nzr * st) * LY + (nzr * ct - ny * st) * LZ
            bright = (0.45 + 0.55 * (0.0 if lam < 0 else 1.0 if lam > 1 else lam)) * gain
            if k == NEEDLE:
                if age < 0.25:                       # white growth front
                    r = g = b = 242
                    bright = 0.9
            elif k == GARLAND:
                bright *= 0.75 + 0.45 * sin(t * 6 + ph) ** 2
        r, g, b = int(r * bright), int(g * bright), int(b * bright)
        R[i], G[i], B[i] = (r if r < 255 else 255), (g if g < 255 else 255), (b if b < 255 else 255)

    def project(x, y, z):
        xr, zr = x * c - z * s, x * s + z * c
        yv, zv = y * ct + zr * st, zr * ct - y * st
        f = CAM / (CAM + zv)
        return int(X0 + xr * f * K), int(YC - yv * f * K), zv, f

    def put(ix, iy, r, g, b):
        if 0 <= ix < RES and 0 <= iy < RES:
            i = iy * RES + ix
            R[i], G[i], B[i] = (r if r < 255 else 255), (g if g < 255 else 255), (b if b < 255 else 255)

    for cx, cy, cz, rad, r, g, b, t0 in sc["balls"]:
        if t0 > t:
            break
        ix, iy, zv, f = project(cx, cy, cz)
        rp = max(1.0, rad * popf((t - t0) / 0.35) * f * K)
        ri = int(rp + 0.5)
        for dy in range(-ri, ri + 1):
            for dx in range(-ri, ri + 1):
                d2 = dx * dx + dy * dy
                if d2 > rp * rp + 1:
                    continue
                xx, yy = ix + dx, iy + dy
                if not (0 <= xx < RES and 0 <= yy < RES) or zv - 0.05 >= depth[yy * RES + xx]:
                    continue
                depth[yy * RES + xx] = zv - 0.05
                sp = max(0.0, 1 - ((dx + 0.4 * rp) ** 2 + (dy + 0.4 * rp) ** 2) / (rp * rp * 0.8 + 0.5)) ** 2
                e = 0.55 + 0.45 * (1 - d2 / (rp * rp + 1))
                put(xx, yy, int(r * e + 255 * sp), int(g * e + 255 * sp), int(b * e + 255 * sp))

    lit = 0
    for x, y, z, r, g, b, t0, ph in sc["lights"]:
        if t0 > t:
            break
        lit += 1
        ix, iy, zv, f = project(x, y, z)
        if not (0 <= ix < RES and 0 <= iy < RES) or zv - 0.05 >= depth[iy * RES + ix]:
            continue
        tw = 0.5 + 0.5 * sin(t * 4 + ph)
        m = (0.55 + 0.6 * tw) * min(1.0, (t - t0) * 3)
        put(ix, iy, int(r * m + 60 * tw), int(g * m + 60 * tw), int(b * m + 60 * tw))
        if tw > 0.35:
            q = 0.5 * m
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                put(ix + dx, iy + dy, int(r * q), int(g * q), int(b * q))

    for u0, v0, sp, ph, big in sc["flakes"]:
        v, u = (v0 + t * sp) % 1.0, (u0 + 0.02 * sin(t * 0.8 + ph)) % 1.0
        ix, iy = int(u * RES), int(v * RES)
        put(ix, iy, 235, 240, 255)
        if big:
            put(ix + 1, iy, 200, 210, 235); put(ix, iy + 1, 200, 210, 235); put(ix + 1, iy + 1, 180, 190, 220)

    out = bytearray(3 * n)
    out[0::3], out[1::3], out[2::3] = R, G, B
    return b"P6 %d %d 255\n" % (RES, RES) + bytes(out), {"lights": lit}


# -------------------------------------------------------------------- GUI
def main():
    import tkinter as tk

    root = tk.Tk()
    root.title("Christmas Tree")
    root.geometry("820x940")
    root.configure(bg="#060810")
    cv = tk.Canvas(root, bg="#060810", highlightthickness=0)
    cv.pack(fill="both", expand=True)
    img_id = cv.create_image(0, 0, anchor="center")
    hud = cv.create_text(12, 10, anchor="nw", fill="#60687a", font=("Consolas", 11), text="")
    help_ = cv.create_text(0, 0, anchor="se", fill="#ff9c4a", font=("Consolas", 11),
                           text="Drag: rotate   Wheel: zoom   Space: pause   ←/→: speed   F: fullscreen   R: restart")
    msg = cv.create_text(0, 0, anchor="s", fill="#ff3b3b", font=("Consolas", 24, "bold"), text="")

    scene = build()
    st = dict(t=0.0, angle=0.0, pitch=TILT, zoom=1.0, speed=1.0, paused=False, last=time.perf_counter(),
              fps=0.0, drag=None, big=None)

    def on_press(e): st["drag"] = (e.x, e.y)
    def on_release(e): st["drag"] = None

    def on_drag(e):
        if st["drag"]:
            dx, dy = e.x - st["drag"][0], e.y - st["drag"][1]
            st["angle"] += dx * 0.01
            st["pitch"] = clamp(st["pitch"] + dy * 0.005, -0.3, 0.95)
            st["drag"] = (e.x, e.y)

    def on_wheel(e):
        up = getattr(e, "delta", 0) > 0 or getattr(e, "num", 0) == 4
        st["zoom"] = clamp(st["zoom"] * (1.1 if up else 1 / 1.1), 0.4, 3.0)

    def toggle_fs(_=None):
        root.attributes("-fullscreen", not root.attributes("-fullscreen"))

    def on_escape(_=None):
        if root.attributes("-fullscreen"):
            root.attributes("-fullscreen", False)
        else:
            root.destroy()

    def pause(_=None): st["paused"] = not st["paused"]
    def faster(_=None): st["speed"] = min(5.0, st["speed"] + 0.25)
    def slower(_=None): st["speed"] = max(-3.0, st["speed"] - 0.25)
    def restart(_=None): st["t"] = 0.0

    cv.bind("<ButtonPress-1>", on_press); cv.bind("<ButtonRelease-1>", on_release); cv.bind("<B1-Motion>", on_drag)
    for ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        cv.bind(ev, on_wheel)
    for key, fn in (("<space>", pause), ("<Right>", faster), ("<Left>", slower), ("<f>", toggle_fs),
                    ("<F11>", toggle_fs), ("<r>", restart), ("<Escape>", on_escape)):
        root.bind(key, fn)

    def tick():
        t_start = time.perf_counter()
        dt = min(0.1, t_start - st["last"])
        st["last"] = t_start
        if not st["paused"]:
            st["t"] += dt
            st["angle"] += SPIN * dt * st["speed"]
        ppm, info = render(scene, st["t"], st["angle"], st["pitch"], st["zoom"])
        cw, ch = max(cv.winfo_width(), 100), max(cv.winfo_height(), 100)
        z = max(1, min(cw, ch) // RES)
        small = tk.PhotoImage(data=ppm, format="PPM")
        st["big"] = small.zoom(z) if z > 1 else small       # keep a reference, or Tk drops the image
        cv.itemconfig(img_id, image=st["big"])
        cv.coords(img_id, cw // 2, ch // 2)

        cv.coords(help_, cw - 12, ch - 10)
        cv.coords(msg, cw // 2, ch - 38)
        cv.itemconfig(msg, font=("Consolas", max(14, min(cw, ch) // 26), "bold"))
        shown = min(len(MESSAGE), int((st["t"] - T_MSG) * 10)) if st["t"] > T_MSG else 0
        cv.itemconfig(msg, text=MESSAGE[:shown], fill=("#ff3b3b", "#ffc24a", "#2fd06a")[int(st["t"] * 1.5) % 3])
        deg = math.degrees(st["angle"]) % 360
        status = "paused" if st["paused"] else "t %05.2fs" % st["t"]
        cv.itemconfig(hud, text="rotation %6.2f°   lights %3d   speed %.2fx   %s   %2.0f fps"
                      % (deg, info["lights"], st["speed"], status, st["fps"]))

        spent = time.perf_counter() - t_start
        st["fps"] = 0.9 * st["fps"] + 0.1 * (1 / max(spent, 1 / 120)) if st["fps"] else 1 / max(spent, 1 / 120)
        root.after(max(1, int(1000 / 60 - spent * 1000)), tick)

    tick()
    root.mainloop()


if __name__ == "__main__":
    main()
