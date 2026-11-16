#!/usr/bin/env python3
"""Generate an animated terminal-style SVG banner (self-hosted, no external fonts)."""
import base64
import codecs
import sys
from html import escape

OUT = sys.argv[1]

W, H = 1000, 470
FS = 15            # terminal font size
CW = FS * 0.602    # approx monospace advance width
LH = 22            # line height
X0 = 36
Y0 = 196           # first terminal line baseline
CYCLE = 16.0       # seconds per full loop

FLAG = "BRK{r3c0n_1s_h4lf_th3_b4ttl3}"
HIDDEN = base64.b64encode(codecs.encode(FLAG, "rot13").encode()).decode()

GREEN, CYAN, MAG, DIM, WHITE, RED, YEL = "#39ff14", "#00e5ff", "#ff2bd6", "#5c6773", "#d7dde4", "#ff4d4d", "#ffd84d"

# (kind, segments, start_time, type_duration)
# kind: "type" = typed command (clip reveal), "show" = output line (instant)
# segments: list of (text, color)
BLUE = "#5c9cff"
PROMPT = [("borakove@ubuntu", GREEN), (":", WHITE), ("~/ops", BLUE), ("$ ", WHITE)]
PROMPT_LEN = sum(len(t) for t, _ in PROMPT)

script = [
    ("type", PROMPT + [("whoami --verbose", WHITE)], 0.4, 1.2),
    ("show", [("[+] ", GREEN), ("Application Security Engineer  //  Penetration Tester  //  Researcher", WHITE)], 2.0, 0),
    ("show", [("[+] ", GREEN), ("10+ yrs  ·  50+ engagements  ·  web · api · mobile · AD · LLM/RAG", DIM)], 2.3, 0),
    ("show", [("", WHITE)], 2.3, 0),
    ("type", PROMPT + [("./chain --from upload --to domain-admin", WHITE)], 3.1, 2.0),
    ("show", [("[*] ", YEL), ("upload ─▶ rce ─▶ pivot ─▶ privesc ─▶ ", WHITE), ("DOMAIN ADMIN", RED)], 5.6, 0),
    ("show", [("[✓] ", GREEN), ("chain validated. writing report + remediation plan...", GREEN)], 6.3, 0),
]


def seg_text(segs):
    out, x = [], 0
    for text, color in segs:
        out.append(f'<tspan fill="{color}">{escape(text)}</tspan>')
        x += len(text)
    return "".join(out), x


def kt(*times):
    return ";".join(f"{min(max(t / CYCLE, 0), 1):.4f}" for t in times)


lines_svg = []
for i, (kind, segs, t0, dur) in enumerate(script):
    y = Y0 + i * LH
    body, nchars = seg_text(segs)
    full_w = nchars * CW + 20
    if kind == "show":
        lines_svg.append(
            f'<text x="{X0}" y="{y}" opacity="0">{body}'
            f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{kt(t0)};{kt(t0 + 0.01)};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></text>'
        )
    else:
        prompt_w = PROMPT_LEN * CW
        cid = f"c{i}"
        lines_svg.append(
            f'<clipPath id="{cid}"><rect x="{X0 - 2}" y="{y - FS}" height="{LH}" width="0">'
            f'<animate attributeName="width" values="0;0;{prompt_w:.1f};{prompt_w:.1f};{full_w:.1f};{full_w:.1f}" '
            f'keyTimes="0;{kt(t0)};{kt(t0 + 0.01)};{kt(t0 + 0.15)};{kt(t0 + 0.15 + dur)};1" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></rect></clipPath>'
            f'<text x="{X0}" y="{y}" clip-path="url(#{cid})">{body}</text>'
        )

# final prompt with blinking cursor
fy = Y0 + len(script) * LH
t_final = 7.0
body, n = seg_text(PROMPT)
lines_svg.append(
    f'<g opacity="0"><text x="{X0}" y="{fy}">{body}</text>'
    f'<rect class="cursor" x="{X0 + PROMPT_LEN * CW:.1f}" y="{fy - FS + 2}" width="{CW:.1f}" height="{FS + 1}" fill="{GREEN}"/>'
    f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{kt(t_final)};{kt(t_final + 0.01)};1" '
    f'dur="{CYCLE}s" repeatCount="indefinite"/></g>'
)

# faint hex dump column on the right (decorative)
hex_rows = []
import random
random.seed(1337)
for r in range(16):
    addr = f"{0x7ffd1337 + r * 16:08x}"
    bytes_ = " ".join(f"{random.randint(0, 255):02x}" for _ in range(4))
    hex_rows.append(f'<text x="800" y="{150 + r * 18}">{addr}  {bytes_}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="borakove — offensive security terminal">
<title>borakove // offensive security</title>
<!-- recon is half the battle. {HIDDEN} -->
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#05070a"/><stop offset="1" stop-color="#0b1117"/>
  </linearGradient>
  <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GREEN}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{GREEN}"/>
  </linearGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#ffffff" opacity=".035"/>
  </pattern>
  <filter id="blur"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<style>
  text {{ font-family: 'JetBrains Mono','Fira Code','DejaVu Sans Mono',Menlo,Consolas,'Courier New',monospace; font-size: {FS}px; white-space: pre; }}
  .logo {{ font-size: 64px; font-weight: 800; letter-spacing: 10px; }}
  .sub  {{ font-size: 13px; letter-spacing: 4px; fill: {DIM}; }}
  .hex  text {{ font-size: 11px; fill: #1f3a2a; }}
  .g1 {{ animation: g1 3.2s infinite steps(1); }}
  .g2 {{ animation: g2 3.2s infinite steps(1); }}
  .cursor {{ animation: blink 1s infinite steps(1); }}
  .sweep {{ animation: sweep 6s linear infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes g1 {{
    0%,86%,100% {{ transform: translate(0,0); opacity: 0; }}
    88% {{ transform: translate(-6px,-2px); opacity: .9; }}
    91% {{ transform: translate(5px,1px); opacity: .9; }}
    94% {{ transform: translate(-3px,2px); opacity: .9; }}
  }}
  @keyframes g2 {{
    0%,86%,100% {{ transform: translate(0,0); opacity: 0; }}
    88% {{ transform: translate(6px,2px); opacity: .9; }}
    91% {{ transform: translate(-5px,-1px); opacity: .9; }}
    94% {{ transform: translate(3px,-2px); opacity: .9; }}
  }}
  @keyframes sweep {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY({H + 40}px); }} }}
</style>

<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#1b2a22"/>

<!-- window chrome -->
<circle cx="26" cy="22" r="6" fill="#ff5f56"/><circle cx="46" cy="22" r="6" fill="#ffbd2e"/><circle cx="66" cy="22" r="6" fill="#27c93f"/>
<text x="{W / 2}" y="27" text-anchor="middle" style="font-size:12px" fill="{DIM}">borakove@ubuntu: ~/ops — bash — 1337×42</text>
<line x1="0" y1="42" x2="{W}" y2="42" stroke="#16211b"/>

<g class="hex">{"".join(hex_rows)}</g>

<!-- glitch logo -->
<g>
  <text x="36" y="118" class="logo" fill="{GREEN}" filter="url(#blur)" opacity=".35">BORAKOVE</text>
  <text x="36" y="118" class="logo g1" fill="{CYAN}">BORAKOVE</text>
  <text x="36" y="118" class="logo g2" fill="{MAG}">BORAKOVE</text>
  <text x="36" y="118" class="logo" fill="url(#glow)">BORAKOVE</text>
  <text x="40" y="146" class="sub">APPSEC · OFFENSIVE SECURITY · EXPLOIT-DRIVEN REMEDIATION</text>
</g>
<line x1="36" y1="166" x2="760" y2="166" stroke="#16211b" stroke-dasharray="2 4"/>

<g>
{chr(10).join(lines_svg)}
</g>

<!-- CRT overlay -->
<rect width="{W}" height="{H}" rx="14" fill="url(#scan)" pointer-events="none"/>
<rect class="sweep" x="0" y="0" width="{W}" height="40" fill="{GREEN}" opacity=".03"/>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("hidden:", HIDDEN)
