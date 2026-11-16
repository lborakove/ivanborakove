#!/usr/bin/env python3
"""
Animated SVG sections for the profile README (run locally, commit the output).

  whoami.svg   - code editor typing the Operator class
  recon.svg    - live nmap scan with a radar discovering ports
  threats.svg  - LLM/RAG threat model: payloads fired at shields
  arsenal.svg  - RPG-style loadout of tools with a roaming cursor
  roe.svg      - rules of engagement checklist, signature and stamp
  ctf.svg      - flag submission terminal

Usage: python3 .github/scripts/sections.py assets [icons_dir]
  icons_dir: folder with simple-icons SVGs (<slug>.svg); downloaded if missing.
"""
import math
import os
import re
import sys
import urllib.request
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import (BG0, BLUE, CYAN, DIM, FAINT, GREEN, MAG, PANEL, RED, TXT,  # noqa: E402
                 YEL, Clock, frame, pix)

STR = "#a5e75a"  # string literal colour
ORANGE = "#ff8c42"


# ───────────────────────────── helpers ─────────────────────────────
def chrome(W, title):
    return (
        f'<circle cx="24" cy="20" r="5.5" fill="#ff5f56"/><circle cx="42" cy="20" r="5.5" fill="#ffbd2e"/>'
        f'<circle cx="60" cy="20" r="5.5" fill="#27c93f"/>'
        f'<text x="{W / 2}" y="24" text-anchor="middle" class="xs" fill="{DIM}">{escape(title)}</text>'
        f'<line x1="0" y1="40" x2="{W}" y2="40" stroke="#121c16"/>'
    )


def spans(segs):
    return "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in segs)


def nchars(segs):
    return sum(len(t) for t, _ in segs)


class Typer:
    """Builds typed (clip-revealed) and instantly-shown lines on a shared clock."""

    def __init__(self, clk, fs):
        self.clk, self.fs, self.cw, self.n = clk, fs, fs * 0.602, 0

    def typed(self, x, y, segs, t0, cps=60, attrs=""):
        self.n += 1
        n = nchars(segs)
        w = n * self.cw + 10
        dur = n / cps
        cid = f"tc{self.n}"
        a = self.clk.anim
        svg = (
            f'<clipPath id="{cid}"><rect x="{x - 2}" y="{y - self.fs - 2}" width="0" height="{self.fs + 8}">'
            f'<animate attributeName="width" values="0;0;{w:.1f};{w:.1f}" keyTimes="{self.clk.kt(0, t0, t0 + dur, self.clk.T)}" {a}/>'
            f'</rect></clipPath><text x="{x}" y="{y}" clip-path="url(#{cid})" {attrs}>{spans(segs)}</text>'
        )
        return svg, t0 + dur

    def shown(self, x, y, segs, t, attrs=""):
        return f'<text x="{x}" y="{y}" opacity="0" {attrs}>{spans(segs)}{self.clk.window(t, self.clk.T, .05)}</text>'


# ───────────────────────────── whoami ─────────────────────────────
def whoami():
    W, FS, LH = 880, 13.5, 23
    q = lambda s: (f'"{s}"', STR)  # noqa: E731
    P, E = ("", TXT), (" = ", DIM)

    def kv(k, *v):
        return [("    ", TXT), (f"{k:<9}", TXT), E, *v]

    def lst(*items):
        out = [("[", TXT)]
        for i, it in enumerate(items):
            out.append(q(it))
            if i < len(items) - 1:
                out.append((", ", TXT))
        return out + [("]", TXT)]

    lines = [
        [("class ", MAG), ("Operator", CYAN), (":", TXT)],
        [("    ", TXT), ('"""offensive by trade, defensive by outcome."""', DIM)],
        kv("handle", q("borakove")),
        kv("roles", *lst("AppSec Engineer", "Penetration Tester", "Security Researcher")),
        kv("path", q("software eng → infrastructure → appsec → offensive security")),
        kv("uptime", q("10+ years")),
        kv("engaged", q("50+ pentests: web · api · mobile · network · active directory")),
        kv("hunting", *lst("HackerOne", "Meli Hacking", "Hack The Box")),
        kv("currently", q("threat modeling LLM/RAG apps & turning scanner noise into real findings")),
        kv("motto", q("if it parses input, it has a bug. find it before they do.")),
    ]
    y0 = 74
    H = y0 + len(lines) * LH + 40
    starts, t = [], 0.6
    clk = Clock(1)  # placeholder to compute durations
    for ln in lines:
        starts.append(t)
        t += nchars(ln) / 75 + 0.18
    T_END = t
    clk = Clock(T_END + 4.5)
    ty = Typer(clk, FS)
    a = clk.anim
    out = [chrome(W, "operator.py — ~/ops — vim")]

    # current-line highlight (discrete jumps)
    ys = [y0 + i * LH - FS - 3 for i in range(len(lines))]
    out.append(
        f'<rect x="0" y="{ys[0]}" width="{W}" height="{LH - 2}" fill="#ffffff" opacity=".035">'
        f'<animate attributeName="y" values="{";".join(str(v) for v in ys)}" '
        f'keyTimes="0;{";".join(f"{s / clk.T:.5f}" for s in starts[1:])}" calcMode="discrete" {a}/></rect>'
        f'<line x1="60" y1="44" x2="60" y2="{H - 30}" stroke="{FAINT}" stroke-opacity=".6"/>'
    )
    for i, ln in enumerate(lines):
        y = y0 + i * LH
        out.append(f'<text x="48" y="{y}" text-anchor="end" class="code" fill="{FAINT}">{i + 1}</text>')
        svg, end = ty.typed(76, y, ln, starts[i], cps=75, attrs='class="code"')
        out.append(svg)
    # cursor after the last line
    last = lines[-1]
    cx = 76 + nchars(last) * ty.cw + 2
    out.append(
        f'<rect x="{cx:.1f}" y="{y0 + (len(lines) - 1) * LH - FS + 1}" width="{ty.cw:.1f}" height="{FS + 2}" fill="{GREEN}" class="blink" opacity="0">'
        f'{clk.window(T_END, clk.T, .01)}</rect>'
    )
    # status bar
    sy = H - 26
    out.append(
        f'<rect x="0" y="{sy}" width="{W}" height="26" fill="#0c1610"/>'
        f'<rect x="0" y="{sy}" width="74" height="26" fill="{GREEN}"/>'
        f'<text x="37" y="{sy + 17}" text-anchor="middle" class="xs" font-weight="700" fill="{BG0}">NORMAL</text>'
        f'<text x="88" y="{sy + 17}" class="xs" fill="{TXT}">operator.py</text>'
        f'<text x="{W - 16}" y="{sy + 17}" text-anchor="end" class="xs" fill="{DIM}">python · utf-8 · LF · {len(lines)}L</text>'
    )
    css = (f".code {{ font-size: {FS}px; }} .blink {{ animation: bl 1s steps(1) infinite; }} "
           f"@keyframes bl {{ 50% {{ fill-opacity: 0; }} }}")
    return frame(W, H, "whoami // operator.py", "Code editor typing a Python class that describes the operator",
                 "\n".join(out), css)


# ───────────────────────────── recon ─────────────────────────────
def recon():
    W, FS, LH, X = 880, 12, 18.5, 24
    ports = [
        ("21/tcp", "recon", "attack-surface mapping · enumeration · OSINT"),
        ("80/tcp", "web-pentest", "OWASP Top 10 · authN/authZ · business logic · file upload → RCE"),
        ("88/tcp", "kerberos", "Active Directory · privilege escalation · domain compromise"),
        ("443/tcp", "api-security", "REST · GraphQL · gRPC · BOLA/BFLA · auth bypass · rate limiting"),
        ("445/tcp", "lateral-mvmt", "internal pivoting · network & firewall assessment"),
        ("5555/tcp", "mobile", "mobile application pentest · backend API abuse"),
        ("8080/tcp", "appsec-sdlc", "secure code review · SAST · DAST · SCA · secrets · security gates"),
        ("9000/tcp", "devsecops", "Jenkins · GitLab CI · GitHub Actions · CheckmarxOne · Acunetix"),
        ("11434/tcp", "llm-redteam", "prompt injection · RAG data leakage · insecure output handling"),
        ("31337/tcp", "elite", "reverse engineering · binary exploitation · CTFs"),
    ]
    prompt = [("borakove@ubuntu", GREEN), (":", TXT), ("~/recon", BLUE), ("$ ", TXT)]
    cmd = prompt + [("nmap -sV -p- --script=skills borakove", TXT)]
    pre = [
        [("Starting Nmap 7.95 ( https://nmap.org )", DIM)],
        [("Nmap scan report for ", DIM), ("borakove", TXT), (" (10.13.37.1)", DIM)],
        [("Host is up ", DIM), ("(0.0001s latency)", GREEN), (" — always on.", DIM)],
    ]
    post = [
        [("OS details: ", DIM), ("Linux (Ubuntu) · Windows (PowerShell) · polyglot: Python C# Java JavaScript SQL Bash", TXT)],
        [("Service Info: ", DIM), ("Mindset: assume-breach; Output: reproducible PoC + practical fix", TXT)],
        [("Nmap done: ", GREEN), ("1 IP address (1 host up) scanned — 0 ports filtered, curiosity unbounded.", GREEN)],
    ]
    y0 = 70
    n_lines = 1 + len(pre) + 2 + len(ports) + 1 + len(post)
    H = int(y0 + (n_lines - 1) * LH + 30)

    t_cmd = 0.5
    t_pre = t_cmd + nchars(cmd[4:]) / 28 + 0.4
    t_hdr = t_pre + len(pre) * 0.3 + 0.3
    t_ports = [t_hdr + 0.5 + i * 0.5 for i in range(len(ports))]
    t_post = t_ports[-1] + 0.6
    T_END = t_post + len(post) * 0.35
    clk = Clock(T_END + 4.5)
    ty = Typer(clk, FS)
    a = clk.anim
    out = [chrome(W, "borakove@ubuntu: ~/recon — bash")]

    y = y0
    # prompt shown instantly, command typed
    out.append(ty.shown(X, y, prompt, 0.2, 'class="mono"'))
    svg, _ = ty.typed(X + nchars(prompt) * ty.cw, y, cmd[4:], t_cmd, cps=28, attrs='class="mono"')
    out.append(svg)
    for i, ln in enumerate(pre):
        y += LH
        out.append(ty.shown(X, y, ln, t_pre + i * 0.3, 'class="mono"'))
    y += LH * 2
    out.append(ty.shown(X, y, [("PORT       STATE  SERVICE        VERSION", DIM)], t_hdr, 'class="mono" font-weight="700"'))
    for i, (p, svc, ver) in enumerate(ports):
        y += LH
        segs = [(f"{p:<11}", CYAN), (f"{'open':<7}", GREEN), (f"{svc:<15}", YEL), (ver, TXT)]
        out.append(ty.shown(X, y, segs, t_ports[i], 'class="mono"'))
    y += LH
    for i, ln in enumerate(post):
        y += LH
        out.append(ty.shown(X, y, ln, t_post + i * 0.35, 'class="mono"'))

    # scan progress line (visible while scanning, replaced by results)
    py = y0 + LH * 4
    out.append(
        f'<g opacity="0">{clk.window(t_hdr - 0.25, t_ports[-1] + .3, .05)}'
        f'<text x="{X}" y="{py}" class="mono" fill="{DIM}">SYN Stealth Scan ·</text>'
        f'<rect x="{X + 150}" y="{py - 9}" width="200" height="8" rx="4" fill="{FAINT}"/>'
        f'<rect x="{X + 150}" y="{py - 9}" width="0" height="8" rx="4" fill="{GREEN}">'
        f'<animate attributeName="width" values="0;0;200;200" keyTimes="{clk.kt(0, t_hdr - .25, t_ports[-1], clk.T)}" {a}/></rect></g>'
    )

    # radar
    cx, cy, r = 800, 122, 60
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r * k / 3:.1f}" fill="none" stroke="{GREEN}" stroke-opacity=".18"/>' for k in (1, 2, 3))
    ang = math.radians(-35)
    wedge = (f'M{cx},{cy} L{cx + r},{cy} A{r},{r} 0 0 0 {cx + r * math.cos(ang):.1f},{cy + r * math.sin(ang):.1f} Z')
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#04110a"/>{rings}'
        f'<line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{GREEN}" stroke-opacity=".12"/>'
        f'<line x1="{cx}" y1="{cy - r}" x2="{cx}" y2="{cy + r}" stroke="{GREEN}" stroke-opacity=".12"/>'
        f'<g><path d="{wedge}" fill="{GREEN}" fill-opacity=".22"/>'
        f'<line x1="{cx}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{GREEN}" stroke-width="1.5"/>'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="2.6s" repeatCount="indefinite"/></g>'
        f'<text x="{cx}" y="{cy + r + 18}" text-anchor="middle" class="xs" fill="{DIM}">TARGET · borakove</text>'
    )
    for i, t in enumerate(t_ports):
        th = math.radians(i * 37 + 20)
        d = r * (0.3 + 0.6 * ((i * 7) % 10) / 10)
        bx, by = cx + d * math.cos(th), cy + d * math.sin(th)
        out.append(
            f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.6" fill="{GREEN}" opacity="0">{clk.window(t, clk.T, .05)}</circle>'
            f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2" fill="none" stroke="{GREEN}" opacity="0">'
            f'<animate attributeName="r" values="2;2;11;11" keyTimes="{clk.kt(0, t, t + .6, clk.T)}" {a}/>'
            f'<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="{clk.kt(0, t, t + .02, t + .6, clk.T)}" {a}/></circle>'
        )
    # open ports counter
    for i in range(len(ports) + 1):
        t0 = t_ports[i - 1] if i else 0
        t1 = t_ports[i] if i < len(ports) else clk.T
        win = clk.window(t0, t1 - 0.001 if t1 < clk.T else clk.T, .001) if i else \
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="{clk.kt(0, t1, t1 + .001, clk.T)}" {a}/>'
        out.append(f'<text x="{cx}" y="{cy - r - 10}" text-anchor="middle" class="xs" fill="{GREEN}" opacity="{1 if i == 0 else 0}">'
                   f'{i:02d} OPEN PORTS{win}</text>')

    css = f".mono {{ font-size: {FS}px; }}"
    return frame(W, H, "recon // nmap", "Animated nmap scan listing skills as open ports", "\n".join(out), css)


# ───────────────────────────── threats ─────────────────────────────
TICONS = {
    "bomb": ["......#..", ".....#...", "...###...", "..#####..", ".#######.", ".##.####.", ".#######.", "..#####..", "...###..."],
    "drop": ["....#....", "...###...", "..#####..", ".#######.", ".#######.", "#########", "###.#####", ".#######.", "..#####.."],
    "flask": ["..#####..", "...#.#...", "...#.#...", "..#...#..", ".#.....#.", "#..###..#", "#.#####.#", "#########", ".#######."],
    "key": [".###.....", "#...#....", "#...#####", "#...#.#.#", ".###..#.#", ".........", ".........", ".........", "........."],
}
SHIELD = ["#########", "#.......#", "#......##", "#.#...#.#", "#..#.#..#", "#...#...#", ".#.....#.", "..#...#..", "...###..."]


def threats():
    W = 880
    rows = [
        ("bomb", "Prompt injection", "direct & indirect", ("user input · poisoned RAG", "docs · tool output"),
         ("retrieved content is data, not orders", "separate instructions from context")),
        ("drop", "Data leakage", "cross-user retrieval", ("retrieval ignores", "who is asking"),
         ("document-level ACLs enforced", "at retrieval time, not in the prompt")),
        ("flask", "Insecure output", "handling", ("model output rendered", "as HTML · SQL · shell"),
         ("model output = untrusted input", "encode · validate · sandbox")),
        ("key", "Broken authz", "excessive agency", ("agents & tools running", "with service-account power"),
         ("least-privilege tools", "propagate the end-user identity")),
    ]
    y0, RH = 92, 76
    H = y0 + len(rows) * RH + 30
    STEP = 1.7
    t_fire = [0.8 + i * STEP for i in range(len(rows))]
    FLY = 1.0
    T_END = t_fire[-1] + FLY + 0.6
    clk = Clock(T_END + 4)
    a = clk.anim
    out = [chrome(W, "~/llm-threat-model — ./redteam --target rag-app")]
    out.append(
        f'<text x="24" y="70" class="cap" fill="{RED}">THREAT</text>'
        f'<text x="380" y="70" text-anchor="middle" class="cap" fill="{DIM}">HOW IT LANDS</text>'
        f'<text x="580" y="70" class="cap" fill="{GREEN}">WHAT ACTUALLY STOPS IT</text>'
    )
    SX, SY_OFF = 548, 22
    for i, (icon, name, sub, vec, ctl) in enumerate(rows):
        y = y0 + i * RH
        t = t_fire[i]
        hit = t + FLY
        ly = y + 30
        # threat card
        out.append(
            f'<rect x="24" y="{y}" width="214" height="58" rx="8" fill="#140a0d" stroke="{RED}" stroke-opacity=".55"/>'
            f'{pix(TICONS[icon], RED, 2.6, 38, y + 17)}'
            f'<text x="74" y="{y + 26}" class="h" fill="{TXT}">{escape(name)}</text>'
            f'<text x="74" y="{y + 43}" class="s" fill="{DIM}">{escape(sub)}</text>'
        )
        # attack lane
        out.append(
            f'<line x1="242" y1="{ly}" x2="{SX - 8}" y2="{ly}" stroke="{RED}" stroke-opacity=".45" class="flow"/>'
            f'<text x="380" y="{ly - 12}" text-anchor="middle" class="s" fill="{DIM}">{escape(vec[0])}</text>'
            f'<text x="380" y="{ly + 20}" text-anchor="middle" class="s" fill="{DIM}">{escape(vec[1])}</text>'
        )
        # payload
        out.append(
            f'<g opacity="0"><circle r="5" fill="{RED}" filter="url(#glow)"/><circle r="2" fill="#fff"/>'
            f'<animateMotion path="M244,{ly} L{SX - 6},{ly}" keyPoints="0;0;1;1" keyTimes="{clk.kt(0, t, hit, clk.T)}" calcMode="linear" {a}/>'
            f'{clk.window(t, hit, .05)}</g>'
        )
        # shield (dim → lit on hit)
        sx, sy = SX, ly - 13
        out.append(
            f'<g opacity=".35">{pix(SHIELD, DIM, 2.9, sx, sy)}</g>'
            f'<g opacity="0" filter="url(#glow)">{pix(SHIELD, GREEN, 2.9, sx, sy)}{clk.window(hit, clk.T, .05)}</g>'
            f'<circle cx="{sx + 13}" cy="{ly}" r="4" fill="none" stroke="{GREEN}" stroke-width="2" opacity="0">'
            f'<animate attributeName="r" values="4;4;26;26" keyTimes="{clk.kt(0, hit, hit + .5, clk.T)}" {a}/>'
            f'<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="{clk.kt(0, hit, hit + .02, hit + .5, clk.T)}" {a}/></circle>'
            f'<g opacity="0">{clk.window(hit + .05, clk.T, .1)}'
            f'<rect x="{sx - 6}" y="{ly + 18}" width="58" height="14" rx="3" fill="{GREEN}"/>'
            f'<text x="{sx + 23}" y="{ly + 28}" text-anchor="middle" class="xs" font-weight="700" fill="{BG0}">BLOCKED</text></g>'
        )
        # control text
        out.append(
            f'<text x="590" y="{ly - 4}" class="s2" fill="{TXT}">{escape(ctl[0])}</text>'
            f'<text x="590" y="{ly + 13}" class="s2" fill="{DIM}">{escape(ctl[1])}</text>'
        )
    out.append(
        f'<g opacity="0">{clk.window(T_END - .3, clk.T, .2)}'
        f'<text x="24" y="{H - 12}" class="s" fill="{GREEN}">✓ {len(rows)}/{len(rows)} attack paths mitigated</text>'
        f'<text x="{W - 24}" y="{H - 12}" text-anchor="end" class="xs" fill="{DIM}">STRIDE · OWASP TOP 10 FOR LLM APPLICATIONS</text></g>'
    )
    css = ".s2 { font-size: 11.5px; }"
    return frame(W, H, "breaking the machines that talk", "LLM/RAG threat model: attacks fired at controls that block them",
                 "\n".join(out), css)


# ───────────────────────────── arsenal ─────────────────────────────
def load_icon(slug, icons_dir):
    path = os.path.join(icons_dir, f"{slug}.svg")
    if not os.path.exists(path):
        os.makedirs(icons_dir, exist_ok=True)
        with urllib.request.urlopen(f"https://cdn.simpleicons.org/{slug}", timeout=20) as r:
            open(path, "wb").write(r.read())
    txt = open(path, encoding="utf-8").read()
    return " ".join(re.findall(r'<path[^>]*\sd="([^"]+)"', txt))


def arsenal(icons_dir):
    W = 880
    cats = [
        ("OFFENSE", GREEN, [
            ("burpsuite", "Burp Suite", "intercept · tamper · repeat. the daily driver"),
            (None, "Acunetix", "DAST at scale, every finding triaged by hand"),
            ("checkmarx", "Checkmarx", "SAST/SCA: separating exploitable from noise"),
            ("owasp", "OWASP", "WSTG · ASVS · API Top 10 · LLM Top 10"),
            ("graphql", "GraphQL", "introspection, batching & authorization abuse"),
            ("android", "Android", "mobile app pentest & backend API abuse"),
            ("ubuntu", "Ubuntu", "home base. bash all the way down"),
        ]),
        ("CODE", CYAN, [
            ("python", "Python", "exploits, tooling & automation"),
            ("dotnet", "C#", "code review & fixes in enterprise .NET"),
            ("openjdk", "Java", "secure code review"),
            ("javascript", "JavaScript", "client-side logic & Node.js review"),
            ("gnubash", "Bash", "the glue for everything"),
            (None, "PowerShell", "Windows & Active Directory tradecraft"),
            (None, "SQL", "injection on one side, the fix on the other"),
        ]),
        ("PIPELINE", MAG, [
            ("jenkins", "Jenkins", "security gates & SCA in CI"),
            ("gitlab", "GitLab CI", "pipeline security"),
            ("githubactions", "Actions", "this profile renders itself with it"),
            ("docker", "Docker", "containers & image scanning"),
            ("kubernetes", "K8s", "cluster security exposure"),
            (None, "AWS", "cloud security exposure"),
            (None, "Azure", "cloud security exposure"),
        ]),
        ("ARENA", YEL, [
            ("hackerone", "HackerOne", "bug bounty"),
            (None, "Meli", "bug bounty program"),
            ("hackthebox", "HTB", "keeping the edge sharp"),
        ]),
    ]
    mono = {"Acunetix": "AX", "PowerShell": "PS", "SQL": "SQL", "AWS": "AWS", "Azure": "AZ", "Meli": "ML"}
    SL, GAP, X0, Y0, RG = 64, 10, 132, 62, 22
    slots = []
    for ci, (cat, col, items) in enumerate(cats):
        y = Y0 + ci * (SL + RG + 6)
        for k, it in enumerate(items):
            slots.append((X0 + k * (SL + GAP), y, col, it))
    play_y = Y0 + len(cats) * (SL + RG + 6) + 10
    H = play_y + 92
    HOP = 0.75
    clk = Clock(len(slots) * HOP)
    a = clk.anim
    out = [chrome(W, "~/loadout — inventory")]

    for ci, (cat, col, items) in enumerate(cats):
        y = Y0 + ci * (SL + RG + 6)
        out.append(f'<text x="24" y="{y + 30}" class="cap" fill="{col}">{cat}</text>'
                   f'<text x="24" y="{y + 46}" class="xs" fill="{FAINT}">{len(items)} slots</text>')
    for i, (x, y, col, (slug, name, _)) in enumerate(slots):
        out.append(f'<rect x="{x}" y="{y}" width="{SL}" height="{SL}" rx="8" fill="{PANEL}" stroke="{FAINT}"/>')
        if slug:
            d = load_icon(slug, icons_dir)
            out.append(f'<g transform="translate({x + SL / 2 - 13},{y + 10}) scale({26 / 24:.4f})"><path d="{d}" fill="{col}"/></g>')
        else:
            out.append(f'<text x="{x + SL / 2}" y="{y + 30}" text-anchor="middle" class="mono2" fill="{col}">{mono[name]}</text>')
        out.append(f'<text x="{x + SL / 2}" y="{y + SL - 9}" text-anchor="middle" class="xs" fill="{DIM}">{escape(name)}</text>')

    # roaming cursor
    xs = ";".join(str(s[0] - 4) for s in slots)
    ys = ";".join(str(s[1] - 4) for s in slots)
    kts = ";".join(f"{i / len(slots):.5f}" for i in range(len(slots)))
    out.append(
        f'<rect x="{slots[0][0] - 4}" y="{slots[0][1] - 4}" width="{SL + 8}" height="{SL + 8}" rx="10" fill="none" '
        f'stroke="{GREEN}" stroke-width="2" filter="url(#glow)">'
        f'<animate attributeName="x" values="{xs}" keyTimes="{kts}" calcMode="discrete" {a}/>'
        f'<animate attributeName="y" values="{ys}" keyTimes="{kts}" calcMode="discrete" {a}/></rect>'
    )
    # tooltip
    ty = play_y - 2
    out.append(f'<rect x="24" y="{ty - 16}" width="{W - 48}" height="26" rx="6" fill="#06110a" stroke="{GREEN}" stroke-opacity=".35"/>')
    for i, (x, y, col, (slug, name, desc)) in enumerate(slots):
        t0, t1 = i * HOP, (i + 1) * HOP
        if i == 0:
            anim = f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="{clk.kt(0, t1 - .001, t1, clk.T)}" {a}/>'
        else:
            anim = (f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                    f'keyTimes="{clk.kt(0, t0 - .001, t0, t1 - .001, t1, clk.T)}" {a}/>')
        out.append(
            f'<text x="36" y="{ty + 1}" class="s" opacity="{1 if i == 0 else 0}"><tspan fill="{GREEN}">&gt; equipped:</tspan> '
            f'<tspan fill="{col}" font-weight="700">{escape(name)}</tspan><tspan fill="{DIM}"> — {escape(desc)}</tspan>{anim}</text>'
        )
    # playbooks & training
    pb = ["PTES", "OWASP WSTG / ASVS", "OWASP API Top 10", "MITRE ATT&CK", "STRIDE"]
    x = 132
    py = play_y + 34
    out.append(f'<text x="24" y="{py + 4}" class="cap" fill="{DIM}">PLAYBOOKS</text>')
    for p in pb:
        w = len(p) * 6.6 + 18
        out.append(f'<rect x="{x}" y="{py - 11}" width="{w:.0f}" height="20" rx="10" fill="none" stroke="{FAINT}"/>'
                   f'<text x="{x + w / 2:.0f}" y="{py + 3}" text-anchor="middle" class="xs" fill="{TXT}">{escape(p)}</text>')
        x += w + 8
    out.append(f'<text x="24" y="{py + 34}" class="cap" fill="{DIM}">TRAINING</text>'
               f'<text x="132" y="{py + 34}" class="s" fill="{TXT}">APIsec University · API Security Architect · OWASP API Top 10 · '
               f'API Gateway · PCI API · API Security in DevSecOps</text>')
    css = ".mono2 { font-size: 15px; font-weight: 800; letter-spacing: 1px; }"
    return frame(W, H, "arsenal // loadout", "Inventory of security tools, languages and platforms", "\n".join(out), css)


# ───────────────────────────── rules of engagement ─────────────────────────────
def roe():
    W = 880
    rules = [
        (True, "authorized scope only. scope is law."),
        (True, "evidence over assumptions: every finding ships with a reproducible PoC"),
        (True, "exploitability over CVSS theater"),
        (True, "a finding without a fix is just a complaint"),
        (True, "responsible disclosure, always"),
        (False, "no unauthorized testing. no exceptions."),
    ]
    y0, LH = 78, 30
    H = y0 + len(rules) * LH + 70
    t_rule = [0.7 + i * 0.75 for i in range(len(rules))]
    t_sign = t_rule[-1] + 0.9
    t_stamp = t_sign + 1.6
    clk = Clock(t_stamp + 4.5)
    a = clk.anim
    out = [chrome(W, "RULES_OF_ENGAGEMENT.md — signed")]
    for i, (ok, text) in enumerate(rules):
        y = y0 + i * LH
        t = t_rule[i]
        col = GREEN if ok else RED
        mark = "✓" if ok else "✗"
        out.append(
            f'<rect x="28" y="{y - 14}" width="18" height="18" rx="4" fill="none" stroke="{FAINT}" stroke-width="1.5"/>'
            f'<g opacity="0">{clk.window(t, clk.T, .05)}'
            f'<rect x="28" y="{y - 14}" width="18" height="18" rx="4" fill="{col}" fill-opacity=".15" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="37" y="{y}" text-anchor="middle" class="h" fill="{col}">{mark}</text></g>'
            f'<text x="60" y="{y}" class="t" fill="{FAINT}">{escape(text)}</text>'
            f'<text x="60" y="{y}" class="t" fill="{TXT if ok else RED}" opacity="0">{escape(text)}{clk.window(t, clk.T, .2)}</text>'
        )
    # signature
    sy = y0 + len(rules) * LH + 26
    sig = ("M96,{y} c8,-22 14,-22 12,-4 c-2,14 6,8 12,-6 c4,-10 8,-6 6,4 c-1,8 6,6 12,-8 "
           "c6,-14 10,-2 8,8 c8,-12 16,-14 18,-2 c2,8 10,0 16,-6 c6,-6 10,0 6,8 "
           "M176,{y2} l70,-6").format(y=sy, y2=sy + 6)
    out.append(
        f'<text x="24" y="{sy + 4}" class="xs" fill="{DIM}">signed:</text>'
        f'<line x1="90" y1="{sy + 10}" x2="320" y2="{sy + 10}" stroke="{FAINT}"/>'
        f'<path d="{sig}" fill="none" stroke="{CYAN}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'stroke-dasharray="420" stroke-dashoffset="420">'
        f'<animate attributeName="stroke-dashoffset" values="420;420;0;0" keyTimes="{clk.kt(0, t_sign, t_sign + 1.3, clk.T)}" {a}/></path>'
        f'<text x="332" y="{sy + 4}" class="xs" fill="{DIM}">borakove · operator</text>'
    )
    # stamp
    stx, sty = 700, y0 + 60
    out.append(
        f'<g opacity="0" transform="translate({stx},{sty}) rotate(-12)">'
        f'<g><rect x="-130" y="-40" width="260" height="80" rx="8" fill="none" stroke="{RED}" stroke-width="4"/>'
        f'<rect x="-122" y="-32" width="244" height="64" rx="5" fill="none" stroke="{RED}" stroke-width="1.5"/>'
        f'<text x="0" y="-4" text-anchor="middle" class="stamp" fill="{RED}">AUTHORIZED</text>'
        f'<text x="0" y="20" text-anchor="middle" class="stamp2" fill="{RED}">SCOPE ONLY</text>'
        f'<animateTransform attributeName="transform" type="scale" values="2.2;2.2;1;1" '
        f'keyTimes="{clk.kt(0, t_stamp, t_stamp + .18, clk.T)}" {a}/></g>'
        f'<animate attributeName="opacity" values="0;0;.92;.92" keyTimes="{clk.kt(0, t_stamp, t_stamp + .12, clk.T)}" {a}/></g>'
    )
    css = (".stamp { font-size: 26px; font-weight: 900; letter-spacing: 5px; } "
           ".stamp2 { font-size: 15px; font-weight: 800; letter-spacing: 8px; }")
    return frame(W, H, "rules of engagement", "Rules of engagement checklist being signed and stamped", "\n".join(out), css)


# ───────────────────────────── ctf ─────────────────────────────
LOCK = ["..#####..", ".#.....#.", ".#.....#.", ".#.....#.", "#########", "#########", "####.####", "####.####", "#########", "#########"]


def ctf():
    W, FS, LH, X = 880, 12.5, 21, 24
    prompt = [("borakove@ubuntu", GREEN), (":", TXT), ("~/ctf", BLUE), ("$ ", TXT)]
    y0 = 72
    H = y0 + 11 * LH + 24
    t_cat = 0.5
    clk = Clock(16)
    ty = Typer(clk, FS)
    a = clk.anim
    out = [chrome(W, "nc profile.borakove 31337")]
    y = y0
    out.append(ty.shown(X, y, prompt, .2, 'class="mono"'))
    svg, t = ty.typed(X + nchars(prompt) * ty.cw, y, [("cat challenge.txt", TXT)], t_cat, cps=24, attrs='class="mono"')
    out.append(svg)
    body = [
        [("  >> a flag is hidden somewhere in this repository.", TXT)],
        [("  format : ", DIM), ("BRK{...}", YEL)],
        [("  hint 1 : ", DIM), ("recon is half the battle. what you see is not all that's served.", TXT)],
        [("  hint 2 : ", DIM), ("two layers. one of them is older than computers.", TXT)],
    ]
    t += 0.3
    for i, ln in enumerate(body):
        y += LH
        out.append(ty.shown(X, y, ln, t + i * 0.25, 'class="mono"'))
    t += len(body) * 0.25 + 0.6
    y += LH * 1.6
    out.append(ty.shown(X, y, prompt, t, 'class="mono"'))
    svg, t2 = ty.typed(X + nchars(prompt) * ty.cw, y, [("./submit_flag", TXT)], t + .2, cps=22, attrs='class="mono"')
    out.append(svg)
    y += LH
    t3 = t2 + 0.4
    out.append(ty.shown(X, y, [("flag> ", MAG), ("BRK{", YEL)], t3, 'class="mono"'))
    # scrambling guess
    import random
    rng = random.Random(31337)
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789_"
    fx = X + 10 * ty.cw
    frames = 10
    for k in range(frames):
        s = "".join(rng.choice(alphabet) for _ in range(22)) + "}"
        f0 = t3 + 0.2 + k * 0.12
        f1 = f0 + 0.12 if k < frames - 1 else clk.T
        out.append(f'<text x="{fx:.1f}" y="{y}" class="mono" fill="{YEL if k == frames - 1 else DIM}" opacity="0">{s}'
                   f'{clk.window(f0, f1 if f1 < clk.T else clk.T, .001)}</text>')
    t4 = t3 + 0.2 + frames * 0.12 + 0.4
    y += LH
    out.append(ty.shown(X, y, [("[!] ", RED), ("access denied — hash mismatch. try harder.", RED)], t4, 'class="mono"'))
    y += LH * 1.6
    out.append(ty.shown(X, y, [("[ connection closed by foreign host ]", DIM)], t4 + 1.0, 'class="mono"'))

    # padlock that shakes on denial
    lx, ly = 770, 96
    out.append(
        f'<g><g filter="url(#glow)">{pix(LOCK, YEL, 7, lx, ly)}</g>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0,0;0,0;-5,0;5,0;-4,0;4,0;0,0;0,0" keyTimes="{clk.kt(0, t4, t4 + .06, t4 + .12, t4 + .18, t4 + .24, t4 + .3, clk.T)}" {a}/></g>'
        f'<text x="{lx + 31}" y="{ly + 96}" text-anchor="middle" class="xs" fill="{DIM}">LOCKED</text>'
    )
    css = f".mono {{ font-size: {FS}px; }}"
    return frame(W, H, "capture the flag", "Flag submission terminal for the hidden profile CTF", "\n".join(out), css)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    icons = sys.argv[2] if len(sys.argv) > 2 else os.path.join(out, ".icons-cache")
    os.makedirs(out, exist_ok=True)
    jobs = [("whoami.svg", whoami), ("recon.svg", recon), ("threats.svg", threats),
            ("arsenal.svg", lambda: arsenal(icons)), ("roe.svg", roe), ("ctf.svg", ctf)]
    for name, fn in jobs:
        with open(os.path.join(out, name), "w", encoding="utf-8") as fh:
            fh.write(fn())
        print("wrote", name)


if __name__ == "__main__":
    main()
