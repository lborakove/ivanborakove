#!/usr/bin/env python3
"""
Static animated SVGs for the profile README (run locally, commit the output).

  assets/killchain.svg  - replay of an attack chain with an escalating impact meter
  assets/pipeline.svg   - AppSec triage "metro map": findings flow from scanners
                          through triage into fix / compensating control / noise

Usage: python3 .github/scripts/art.py assets
"""
import os
import sys
from html import escape

BG0, BG1, BORDER = "#05070a", "#0b1117", "#1b2a22"
GREEN, CYAN, MAG, RED, YEL, BLUE = "#39ff14", "#00e5ff", "#ff2bd6", "#ff3b5c", "#ffd84d", "#5c9cff"
TXT, DIM, FAINT, PANEL = "#d7dde4", "#6b7785", "#2a3540", "#0d141b"
FONT = "'JetBrains Mono','Fira Code','DejaVu Sans Mono',Menlo,Consolas,'Courier New',monospace"


def frame(W, H, title, label, body, extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(label)}">
<title>{escape(title)}</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".03"/></pattern>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#16212b"/></pattern>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  text {{ font-family: {FONT}; }}
  .t {{ font-size: 13px; }} .s {{ font-size: 10.5px; }} .xs {{ font-size: 9px; letter-spacing: .6px; }}
  .h {{ font-size: 11.5px; font-weight: 700; }} .cap {{ font-size: 10px; letter-spacing: 2.5px; font-weight: 700; }}
  .flow {{ stroke-dasharray: 3 5; animation: flow 1s linear infinite; }}
  @keyframes flow {{ to {{ stroke-dashoffset: -8; }} }}
  {extra_css}
</style>
<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>
<rect width="{W}" height="{H}" rx="12" fill="url(#dots)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{BORDER}"/>
{body}
<rect width="{W}" height="{H}" rx="12" fill="url(#scan)"/>
</svg>
'''


class Clock:
    def __init__(self, T):
        self.T = T
        self.anim = f'dur="{T:.2f}s" repeatCount="indefinite"'

    def kt(self, *ts):
        out, last = [], 0.0
        for t in ts:
            v = max(min(max(t / self.T, 0.0), 1.0), last)
            out.append(v)
            last = v
        return ";".join(f"{v:.5f}" for v in out)

    def window(self, t0, t1, fade=0.15):
        """opacity animation: hidden → visible in [t0, t1] → hidden."""
        T = self.T
        if t1 >= T:
            return f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="{self.kt(0, t0, t0 + fade, T)}" {self.anim}/>'
        return (f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="{self.kt(0, t0, t0 + fade, t1, t1 + fade, T)}" {self.anim}/>')


def pix(rows, color, px, x0=0, y0=0):
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x] != "#":
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == "#":
                run += 1
            out.append(f'<rect x="{x0 + x * px:g}" y="{y0 + y * px:g}" width="{run * px:g}" height="{px:g}" fill="{color}"/>')
            x += run
    return "".join(out)


ICONS = {
    "recon": ["..###....", ".#...#...", "#.....#..", "#..#..#..", "#.....#..", ".#...#...", "..####...", "......##.", ".......##"],
    "upload": ["....#....", "...###...", "..#####..", ".#..#..#.", "....#....", "....#....", ".........", "#.......#", "#########"],
    "rce": ["#########", "#.......#", "#.#.....#", "#..#....#", "#.#..##.#", "#.......#", "#########", "...###...", ".#######."],
    "pivot": ["##.....##", "##.....##", "..#...#..", "...#.#...", "....#....", "...#.#...", "..#...#..", "##.....##", "##.....##"],
    "privesc": ["....#....", "...###...", "..#####..", ".#######.", "...###...", "...###...", "...###...", "...###...", "...###..."],
    "crown": [".........", "#...#...#", "##.###.##", "#########", "#########", "#########", ".#######.", ".........", "#########"],
    "report": ["######...", "#....##..", "#.....#..", "#.###.#..", "#.....#..", "#.##..#.#", "#.....##.", "#.....#..", "#######.."],
}


# ───────────────────────────── kill chain ─────────────────────────────
def killchain():
    W, H = 880, 280
    steps = [
        ("recon", "TA0043", "Recon", "attack surface", "mapping", CYAN),
        ("upload", "TA0001", "Initial Access", "insecure file", "upload", GREEN),
        ("rce", "TA0002", "Execution", "webshell →", "remote shell", GREEN),
        ("pivot", "TA0008", "Lateral Mvmt", "pivot into the", "internal net", GREEN),
        ("privesc", "TA0004", "Priv Esc", "misconfig →", "local admin", GREEN),
        ("crown", "TA0006", "Domain Admin", "full domain", "compromise", RED),
        ("report", "FIX", "Report+Retest", "root cause fix", "verified ✓", YEL),
    ]
    n = len(steps)
    cw, gap, x0, y0, ch = 106, 16, 0, 78, 128
    x0 = (W - (n * cw + (n - 1) * gap)) / 2
    STEP_T, T0 = 1.5, 0.9
    t_on = [T0 + i * STEP_T for i in range(n)]
    T_END = t_on[-1] + 1.0
    clk = Clock(T_END + 3.4)
    a = clk.anim
    out = []

    out.append(
        f'<text x="24" y="31" class="t" fill="{DIM}">~/ops <tspan fill="{CYAN}">$</tspan> '
        f'<tspan fill="{TXT}">./chain --replay</tspan> <tspan fill="{GREEN}">engagement-0x2a</tspan></text>'
        f'<text x="{W - 24}" y="31" text-anchor="end" class="xs" fill="{DIM}">SANITIZED · NO CLIENT DATA · MITRE ATT&amp;CK TACTICS</text>'
        f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="#121c16"/>'
    )

    # connectors (behind cards)
    cy = y0 + 44
    for i in range(n - 1):
        xa = x0 + i * (cw + gap) + cw
        xb = xa + gap
        out.append(f'<line x1="{xa:.1f}" y1="{cy}" x2="{xb:.1f}" y2="{cy}" stroke="{FAINT}" stroke-width="2"/>')
        col = steps[i + 1][5]
        out.append(
            f'<line x1="{xa:.1f}" y1="{cy}" x2="{xb:.1f}" y2="{cy}" stroke="{col}" stroke-width="2" opacity="0">'
            f'{clk.window(t_on[i + 1] - 0.25, clk.T)}</line>'
        )

    for i, (icon, tag, title, d1, d2, col) in enumerate(steps):
        x = x0 + i * (cw + gap)
        t = t_on[i]
        cx = x + cw / 2
        # base (dim) card
        out.append(
            f'<rect x="{x:.1f}" y="{y0}" width="{cw}" height="{ch}" rx="8" fill="{PANEL}" stroke="{FAINT}"/>'
            f'<g opacity=".28">{pix(ICONS[icon], DIM, 3, cx - 13.5, y0 + 30)}</g>'
            f'<text x="{cx:.1f}" y="{y0 + 18}" text-anchor="middle" class="xs" fill="{FAINT}">{tag}</text>'
            f'<text x="{cx:.1f}" y="{y0 + 80}" text-anchor="middle" class="h" fill="{DIM}">{escape(title)}</text>'
            f'<text x="{cx:.1f}" y="{y0 + 99}" text-anchor="middle" class="s" fill="{FAINT}">{escape(d1)}</text>'
            f'<text x="{cx:.1f}" y="{y0 + 113}" text-anchor="middle" class="s" fill="{FAINT}">{escape(d2)}</text>'
        )
        # lit overlay
        fill = "#1a0a0e" if col == RED else ("#191505" if col == YEL else PANEL)
        out.append(
            f'<g opacity="0">'
            f'<rect x="{x:.1f}" y="{y0}" width="{cw}" height="{ch}" rx="8" fill="{fill}" stroke="{col}" stroke-width="1.6" filter="url(#glow)"/>'
            f'<g filter="url(#glow)">{pix(ICONS[icon], col, 3, cx - 13.5, y0 + 30)}</g>'
            f'<text x="{cx:.1f}" y="{y0 + 18}" text-anchor="middle" class="xs" fill="{col}">{tag}</text>'
            f'<text x="{cx:.1f}" y="{y0 + 80}" text-anchor="middle" class="h" fill="{TXT}">{escape(title)}</text>'
            f'<text x="{cx:.1f}" y="{y0 + 99}" text-anchor="middle" class="s" fill="{DIM}">{escape(d1)}</text>'
            f'<text x="{cx:.1f}" y="{y0 + 113}" text-anchor="middle" class="s" fill="{DIM}">{escape(d2)}</text>'
            f'{clk.window(t, clk.T)}</g>'
        )
        # flash ring when the stage pops
        out.append(
            f'<rect x="{x:.1f}" y="{y0}" width="{cw}" height="{ch}" rx="8" fill="none" stroke="{col}" stroke-width="2" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="{clk.kt(0, t, t + .03, t + .6, clk.T)}" {a}/></rect>'
        )

    # payload packet travelling across the chain
    xs = [x0 + i * (cw + gap) + cw / 2 for i in range(n)]
    path = "M" + " L".join(f"{x:.1f},{cy}" for x in xs)
    kp = ";".join(f"{(xx - xs[0]) / (xs[-1] - xs[0]):.4f}" for xx in xs)
    kts = clk.kt(*t_on)
    out.append(
        f'<g opacity="0"><circle r="5" fill="{GREEN}" filter="url(#glow)"/><circle r="2" fill="#fff"/>'
        f'<animateMotion path="{path}" keyPoints="0;{kp};1;1" keyTimes="0;{kts};{clk.kt(T_END)};1" calcMode="linear" {a}/>'
        f'{clk.window(t_on[0], t_on[-1] - 0.2, 0.05)}</g>'
    )

    # impact meter
    my = y0 + ch + 34
    mx, mw = 24 + 86, W - 48 - 86 - 300
    levels = [  # (stage index, fraction, colour, label)
        (0, 0.08, CYAN, "LOW — just looking"),
        (1, 0.40, YEL, "MEDIUM — “it's just a file upload”"),
        (2, 0.66, "#ff8c42", "HIGH — code execution on the web tier"),
        (3, 0.74, "#ff8c42", "HIGH — foothold inside the network"),
        (4, 0.88, RED, "CRITICAL — admin on internal hosts"),
        (5, 1.00, RED, "CRITICAL — the whole domain is owned"),
        (6, 1.00, GREEN, "REMEDIATED — retest passed, chain broken"),
    ]
    out.append(
        f'<text x="24" y="{my + 9}" class="cap" fill="{DIM}">IMPACT</text>'
        f'<rect x="{mx}" y="{my}" width="{mw}" height="10" rx="5" fill="{FAINT}"/>'
    )
    for k in range(1, 4):
        out.append(f'<line x1="{mx + mw * k / 4:.1f}" y1="{my - 3}" x2="{mx + mw * k / 4:.1f}" y2="{my + 13}" stroke="#05070a" stroke-width="2"/>')
    wv = ";".join(["0", "0"] + [f"{mw * lv[1]:.1f}" for lv in levels] + [f"{mw:.1f}"])
    wk = clk.kt(0, t_on[0] - 0.01, *t_on, clk.T)
    cv = ";".join([CYAN, CYAN] + [lv[2] for lv in levels] + [GREEN])
    out.append(
        f'<rect x="{mx}" y="{my}" width="0" height="10" rx="5" fill="{CYAN}">'
        f'<animate attributeName="width" values="{wv}" keyTimes="{wk}" {a}/>'
        f'<animate attributeName="fill" values="{cv}" keyTimes="{wk}" calcMode="discrete" {a}/></rect>'
    )
    for j, (si, _, col, label) in enumerate(levels):
        t0 = t_on[si]
        t1 = t_on[si + 1] if si + 1 < n else clk.T
        out.append(
            f'<text x="{mx + mw + 16}" y="{my + 9}" class="s" fill="{col}" font-weight="700" opacity="0">{escape(label)}'
            f'{clk.window(t0, t1 - 0.05 if t1 < clk.T else clk.T, 0.08)}</text>'
        )
    for k, lab in enumerate(["LOW", "MED", "HIGH", "CRIT"]):
        out.append(f'<text x="{mx + mw * (k + .5) / 4:.1f}" y="{my + 28}" text-anchor="middle" class="xs" fill="{FAINT}">{lab}</text>')

    return frame(W, H, "kill chain // replay", "Animated attack chain from recon to domain admin, then remediation",
                 "\n".join(out))


# ───────────────────────────── pipeline ─────────────────────────────
def pipeline():
    W, H = 880, 320
    LY = {"real": 92, "comp": 170, "noise": 254}
    LCOL = {"real": RED, "comp": YEL, "noise": DIM}
    TRX, TRY = 380, 170          # triage centre
    SX = 214                      # chips spawn here
    BR = 488                      # lanes branch here
    GATE_X = 820
    findings = [
        ("SQLi · /api/search", "real"),
        ("XSS · escaped tmpl", "noise"),
        ("CVE · unreachable", "noise"),
        ("hardcoded secret", "real"),
        ("IDOR · /orders/{id}", "real"),
        ("path trav. · const", "noise"),
        ("legacy crypto", "comp"),
        ("open redirect · FP", "noise"),
    ]
    CW, CH = 128, 20
    SPAWN, TO_TRI, HOLD, LANE = 2.2, 1.3, 0.8, 2.8
    clk = Clock(0.6 + (len(findings) - 1) * SPAWN + TO_TRI + HOLD + LANE + 1.4)
    a = clk.anim
    out = []

    out.append(
        f'<text x="24" y="31" class="t" fill="{DIM}">~/pipeline <tspan fill="{CYAN}">$</tspan> '
        f'<tspan fill="{TXT}">triage --exploitability</tspan> <tspan fill="{GREEN}">--no-cvss-theater</tspan></text>'
        f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="#121c16"/>'
    )

    # scanners column
    scanners = ["SAST", "SCA", "DAST", "SECRETS", "CONTAINERS"]
    out.append(f'<text x="24" y="76" class="cap" fill="{DIM}">git push ⟶ scan</text>')
    for i, s in enumerate(scanners):
        y = 90 + i * 32
        out.append(
            f'<rect x="24" y="{y}" width="118" height="22" rx="11" fill="{PANEL}" stroke="{FAINT}"/>'
            f'<circle cx="38" cy="{y + 11}" r="3.5" fill="{CYAN}"><animate attributeName="opacity" values="1;.2;1" dur="{1.2 + i * .25:.2f}s" repeatCount="indefinite"/></circle>'
            f'<text x="50" y="{y + 15}" class="s" fill="{TXT}">{s}</text>'
            f'<path d="M142,{y + 11} C170,{y + 11} 170,{TRY} 196,{TRY}" fill="none" stroke="{FAINT}" class="flow"/>'
        )

    # lanes
    out.append(f'<line x1="{SX - 18}" y1="{TRY}" x2="{TRX - 90}" y2="{TRY}" stroke="{FAINT}" stroke-width="3"/>')
    for lane, y in LY.items():
        end = GATE_X if lane != "noise" else 760
        d = f"M{TRX + 90},{TRY} L{BR},{TRY} L{BR},{y} L{end},{y}" if y != TRY else f"M{TRX + 90},{TRY} L{end},{y}"
        out.append(f'<path d="{d}" fill="none" stroke="{LCOL[lane]}" stroke-opacity=".35" stroke-width="3" stroke-linejoin="round"/>')

    # stations (label above the line)
    stations = [
        ("real", 552, "PoC + severity", "real-world impact"),
        ("real", 678, "fix w/ dev team", "root cause"),
        ("comp", 630, "compensating ctrl", "+ tracked exception"),
        ("noise", 600, "rule tuned", "rationale documented"),
    ]
    for lane, x, l1, l2 in stations:
        y = LY[lane]
        out.append(
            f'<circle cx="{x}" cy="{y}" r="6" fill="{BG0}" stroke="{LCOL[lane]}" stroke-width="2.5"/>'
            f'<text x="{x}" y="{y - 26}" text-anchor="middle" class="s" fill="{TXT}">{l1}</text>'
            f'<text x="{x}" y="{y - 14}" text-anchor="middle" class="xs" fill="{DIM}">{l2}</text>'
        )
    out.append(
        f'<text x="776" y="{LY["noise"] + 4}" class="s" fill="{DIM}">/dev/null</text>'
        f'<text x="{BR + 8}" y="{LY["real"] + 26}" class="xs" fill="{RED}">EXPLOITABLE</text>'
        f'<text x="{BR + 8}" y="{LY["comp"] + 22}" class="xs" fill="{YEL}">CAN\'T PATCH YET</text>'
        f'<text x="{BR + 8}" y="{LY["noise"] + 22}" class="xs" fill="{DIM}">FALSE POSITIVE</text>'
    )

    # triage box
    out.append(
        f'<text x="{TRX}" y="{TRY - 44}" text-anchor="middle" class="cap" fill="{CYAN}">TRIAGE</text>'
        f'<rect x="{TRX - 90}" y="{TRY - 32}" width="180" height="64" rx="10" fill="{PANEL}" stroke="{CYAN}" stroke-opacity=".6"/>'
        f'<text x="{TRX}" y="{TRY + 50}" text-anchor="middle" class="xs" fill="{DIM}">read the code · reach the sink · prove it</text>'
        f'<rect x="{TRX - 88}" y="{TRY - 30}" width="4" height="60" fill="{CYAN}" opacity=".35">'
        f'<animate attributeName="x" values="{TRX - 88};{TRX + 84};{TRX - 88}" dur="2.4s" repeatCount="indefinite"/></rect>'
    )

    # security gate
    out.append(
        f'<rect x="{GATE_X}" y="62" width="34" height="140" rx="6" fill="#06180c" stroke="{GREEN}" stroke-opacity=".7"/>'
        f'<text transform="translate({GATE_X + 21},132) rotate(-90)" text-anchor="middle" class="cap" fill="{GREEN}">GATE ✓</text>'
    )

    # findings
    counts = {"real": 0, "comp": 0, "noise": 0}
    gate_hits = []
    for i, (label, lane) in enumerate(findings):
        counts[lane] += 1
        t0 = 0.6 + i * SPAWN
        t_tri = t0 + TO_TRI
        t_dec = t_tri + HOLD
        t_end = t_dec + LANE
        y = LY[lane]
        end_x = GATE_X - 116 if lane != "noise" else 700
        pts = [(SX, TRY), (TRX, TRY), (BR, TRY)] + ([(BR, y)] if y != TRY else []) + [(end_x, y)]
        d = "M" + " L".join(f"{x:.0f},{yy:.0f}" for x, yy in pts)
        seg = [abs(b[0] - a_[0]) + abs(b[1] - a_[1]) for a_, b in zip(pts, pts[1:])]
        tot = sum(seg)
        p_tri = seg[0] / tot
        col0, col1 = "#8b949e", LCOL[lane]
        fix_t = None
        if lane == "real":  # turns green once it passes the "fix" station
            fix_t = t_dec + LANE * (seg[1] + seg[2] + (678 - BR)) / (tot - seg[0])
            gate_hits.append(t_end)
        elif lane == "comp":
            gate_hits.append(t_end)
        strokes = [col0, col0, col1, col1] + ([GREEN, GREEN] if fix_t else [])
        stimes = [0, t_tri + .2, t_tri + .35, (fix_t or clk.T)] + ([fix_t + .1, clk.T] if fix_t else [])
        if not fix_t:
            strokes, stimes = strokes[:3] + [col1], stimes[:3] + [clk.T]
        verdict = {"real": "VULN", "comp": "RISK", "noise": "FP"}[lane]
        out.append(
            f'<g opacity="0">'
            f'<rect x="{-CW / 2}" y="{-CH / 2}" width="{CW}" height="{CH}" rx="4" fill="#0a0f14" stroke="{col0}" stroke-width="1.4">'
            f'<animate attributeName="stroke" values="{";".join(strokes)}" keyTimes="{clk.kt(*stimes)}" {a}/></rect>'
            f'<text x="{-CW / 2 + 8}" y="4" class="s" fill="{TXT}">{escape(label)}</text>'
            f'<g opacity="0"><rect x="{CW / 2 + 4}" y="-7" width="{len(verdict) * 7 + 8}" height="14" rx="3" fill="{col1 if lane != "noise" else FAINT}"/>'
            f'<text x="{CW / 2 + 8}" y="3.5" class="xs" font-weight="700" fill="{BG0 if lane != "noise" else TXT}">{verdict}</text>'
            f'{clk.window(t_tri + .25, fix_t or t_end, .1)}</g>'
            + (f'<g opacity="0"><rect x="{CW / 2 + 4}" y="-7" width="43" height="14" rx="3" fill="{GREEN}"/>'
               f'<text x="{CW / 2 + 8}" y="3.5" class="xs" font-weight="700" fill="{BG0}">FIXED</text>'
               f'{clk.window(fix_t + .1, t_end, .1)}</g>' if fix_t else "") +
            f'<animateMotion path="{d}" keyPoints="0;0;{p_tri:.4f};{p_tri:.4f};1;1" '
            f'keyTimes="{clk.kt(0, t0, t_tri, t_dec, t_end, clk.T)}" calcMode="linear" {a}/>'
            f'<animate attributeName="opacity" values="0;0;1;1;{".25" if lane == "noise" else "1"};0;0" '
            f'keyTimes="{clk.kt(0, t0, t0 + .2, t_dec, t_end - .3, t_end, clk.T)}" {a}/>'
            f'</g>'
        )

    # gate pulses
    for t in gate_hits:
        out.append(
            f'<rect x="{GATE_X}" y="62" width="34" height="140" rx="6" fill="{GREEN}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;.45;0;0" keyTimes="{clk.kt(0, t - .05, t, t + .5, clk.T)}" {a}/></rect>'
        )

    total = len(findings)
    out.append(
        f'<text x="24" y="{H - 18}" class="s" fill="{DIM}">'
        f'<tspan fill="{TXT}">{total}</tspan> findings in  ⟶  '
        f'<tspan fill="{RED}">{counts["real"]} exploitable</tspan> → fixed  ·  '
        f'<tspan fill="{YEL}">{counts["comp"]} compensated</tspan>  ·  '
        f'<tspan fill="{TXT}">{counts["noise"]} false positives</tspan> silenced with rationale</text>'
    )

    return frame(W, H, "from red to blue // triage", "Animated AppSec triage pipeline", "\n".join(out))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(out, exist_ok=True)
    for name, fn in (("killchain.svg", killchain), ("pipeline.svg", pipeline)):
        with open(os.path.join(out, name), "w", encoding="utf-8") as fh:
            fh.write(fn())
        print("wrote", name)


if __name__ == "__main__":
    main()
