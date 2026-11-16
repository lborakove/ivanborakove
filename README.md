<div align="center">

<img src="./assets/banner.svg" alt="borakove — offensive security terminal" width="100%"/>

<br/>

![AppSec](https://img.shields.io/badge/AppSec-0d1117?style=flat-square&logo=owasp&logoColor=39ff14&labelColor=0d1117&color=0d1117)
![Pentest](https://img.shields.io/badge/Penetration_Testing-0d1117?style=flat-square&logo=ubuntu&logoColor=39ff14)
![Red Team Mindset](https://img.shields.io/badge/Red_Team_Mindset-0d1117?style=flat-square&logo=hackthebox&logoColor=39ff14)
![LLM Security](https://img.shields.io/badge/LLM%2FRAG_Security-0d1117?style=flat-square&logo=probot&logoColor=39ff14)
![Profile hits](https://komarev.com/ghpvc/?username=lborakove&label=PACKETS%20RECEIVED&color=0d1117&style=flat-square)

<sub><code>// break it in the lab, prove it with a PoC, fix it in the pipeline //</code></sub>

</div>

---

### `0x00` &nbsp;// whoami

```python
class Operator:
    handle    = "borakove"
    roles     = ["AppSec Engineer", "Penetration Tester", "Security Researcher"]
    path      = "software eng → infrastructure → appsec → offensive security"
    uptime    = "10+ years"
    engaged   = "50+ pentests: web · api · mobile · network · active directory"
    hunting   = ["HackerOne", "Meli Hacking", "Hack The Box"]
    currently = "threat modeling LLM/RAG apps & turning scanner noise into real findings"
    motto     = "if it parses input, it has a bug. find it before they do."
```

---

### `0x01` &nbsp;// recon

```console
$ nmap -sV -p- --script=skills borakove
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for borakove (10.13.37.1)
Host is up (0.0001s latency) — always on.

PORT       STATE  SERVICE          VERSION
21/tcp     open   recon            attack-surface mapping · enumeration · OSINT
80/tcp     open   web-pentest      OWASP Top 10 · authN/authZ · business logic · file upload → RCE
88/tcp     open   kerberos         Active Directory · privilege escalation · domain compromise
443/tcp    open   api-security     REST · GraphQL · gRPC · BOLA/BFLA · auth bypass · rate limiting
445/tcp    open   lateral-mvmt     internal pivoting · network & firewall assessment
5555/tcp   open   mobile           mobile application pentest · backend API abuse
8080/tcp   open   appsec-sdlc      secure code review · SAST · DAST · SCA · secrets · security gates
9000/tcp   open   devsecops        Jenkins · GitLab CI · GitHub Actions · CheckmarxOne · Acunetix
11434/tcp  open   llm-redteam      prompt injection · RAG data leakage · insecure output handling
31337/tcp  open   elite            reverse engineering · binary exploitation · CTFs

OS details: Linux (Ubuntu) · Windows (PowerShell) · polyglot: Python C# Java JavaScript SQL Bash
Service Info: Mindset: assume-breach; Output: reproducible PoC + practical fix

Nmap done: 1 IP address (1 host up) scanned — 0 ports filtered, curiosity unbounded.
```

---

### `0x02` &nbsp;// kill chain

> A pattern I've demonstrated in real engagements (sanitized, no client data). One weak upload form is rarely "just a medium".

```mermaid
flowchart LR
    A["🔍 Recon<br/>surface mapping"] --> B["📤 Insecure<br/>File Upload"]
    B --> C["💥 Remote Code<br/>Execution"]
    C --> D["🔀 Internal<br/>Pivoting"]
    D --> E["⬆️ Privilege<br/>Escalation"]
    E --> F["👑 Domain<br/>Admin"]
    F --> G["📝 Report<br/>+ Retest"]

    classDef recon  fill:#0d1117,stroke:#00e5ff,color:#c9d1d9,stroke-width:2px;
    classDef attack fill:#0d1117,stroke:#39ff14,color:#c9d1d9,stroke-width:2px;
    classDef crown  fill:#2a0b0b,stroke:#ff4d4d,color:#ffdddd,stroke-width:3px;
    classDef fix    fill:#0b1a2a,stroke:#ffd84d,color:#fff3c4,stroke-width:2px;
    class A recon;
    class B,C,D,E attack;
    class F crown;
    class G fix;
```

---

### `0x03` &nbsp;// from red to blue

Offense only matters if it ends in a fix. On the AppSec side, I'm the person who decides whether a SAST alert is a real exploit or noise:

```mermaid
flowchart LR
    commit["git push"] --> scan{{"SAST · SCA · DAST<br/>containers · secrets"}}
    scan --> triage{"exploitable?"}
    triage -- "no: false positive" --> tune["tune rules<br/>document rationale"]
    triage -- "yes" --> poc["PoC + severity<br/>(real-world impact)"]
    poc --> fix["fix with the dev team"]
    fix --> gate["security gate ✅"]
    poc -. "can't patch the code yet" .-> comp["compensating controls<br/>+ controlled exception"]
    comp --> gate

    classDef n fill:#0d1117,stroke:#39ff14,color:#c9d1d9;
    classDef d fill:#0d1117,stroke:#00e5ff,color:#c9d1d9;
    classDef w fill:#1a1405,stroke:#ffd84d,color:#fff3c4;
    class commit,tune,poc,fix,gate n;
    class scan,triage d;
    class comp w;
```

---

### `0x04` &nbsp;// breaking the machines that talk

LLM features are just new parsers with an English-shaped attack surface. How I threat model LLM/RAG apps:

| Threat | How it lands | What actually stops it |
|:--|:--|:--|
| 🧨 **Prompt injection** (direct & indirect) | user input, poisoned docs in the RAG index, tool output | treat all retrieved content as data; privilege separation between instructions and context |
| 🕳️ **Data leakage** | retrieval ignores who is asking | enforce document-level ACLs **at retrieval time**, not in the prompt |
| 🧪 **Insecure output handling** | model output rendered as HTML, SQL or shell | the model's output is untrusted input: encode, validate, sandbox |
| 🔑 **Broken authorization** | agents and tools running with service-account power | least-privilege tools, propagate the end-user's identity |

---

### `0x05` &nbsp;// arsenal

<p>
<img src="https://img.shields.io/badge/Burp_Suite-0d1117?style=for-the-badge&logo=burpsuite&logoColor=39ff14"/>
<img src="https://img.shields.io/badge/Ubuntu-0d1117?style=for-the-badge&logo=ubuntu&logoColor=39ff14"/>
<img src="https://img.shields.io/badge/CheckmarxOne-0d1117?style=for-the-badge&logo=checkmarx&logoColor=39ff14"/>
<img src="https://img.shields.io/badge/Acunetix-0d1117?style=for-the-badge&logo=target&logoColor=39ff14"/>
<img src="https://img.shields.io/badge/OWASP-0d1117?style=for-the-badge&logo=owasp&logoColor=39ff14"/>
<img src="https://img.shields.io/badge/GraphQL-0d1117?style=for-the-badge&logo=graphql&logoColor=39ff14"/>
<img src="https://img.shields.io/badge/Android-0d1117?style=for-the-badge&logo=android&logoColor=39ff14"/>
</p>

<p>
<img src="https://img.shields.io/badge/Python-0d1117?style=for-the-badge&logo=python&logoColor=00e5ff"/>
<img src="https://img.shields.io/badge/C%23-0d1117?style=for-the-badge&logo=dotnet&logoColor=00e5ff"/>
<img src="https://img.shields.io/badge/Java-0d1117?style=for-the-badge&logo=openjdk&logoColor=00e5ff"/>
<img src="https://img.shields.io/badge/JavaScript-0d1117?style=for-the-badge&logo=javascript&logoColor=00e5ff"/>
<img src="https://img.shields.io/badge/Bash-0d1117?style=for-the-badge&logo=gnubash&logoColor=00e5ff"/>
<img src="https://img.shields.io/badge/PowerShell-0d1117?style=for-the-badge&logo=gnometerminal&logoColor=00e5ff"/>
<img src="https://img.shields.io/badge/SQL-0d1117?style=for-the-badge"/>
</p>

<p>
<img src="https://img.shields.io/badge/Jenkins-0d1117?style=for-the-badge&logo=jenkins&logoColor=ff2bd6"/>
<img src="https://img.shields.io/badge/GitLab_CI-0d1117?style=for-the-badge&logo=gitlab&logoColor=ff2bd6"/>
<img src="https://img.shields.io/badge/GitHub_Actions-0d1117?style=for-the-badge&logo=githubactions&logoColor=ff2bd6"/>
<img src="https://img.shields.io/badge/Docker-0d1117?style=for-the-badge&logo=docker&logoColor=ff2bd6"/>
<img src="https://img.shields.io/badge/Kubernetes-0d1117?style=for-the-badge&logo=kubernetes&logoColor=ff2bd6"/>
<img src="https://img.shields.io/badge/AWS_%2F_Azure-0d1117?style=for-the-badge"/>
</p>

<p>
<img src="https://img.shields.io/badge/HackerOne-0d1117?style=for-the-badge&logo=hackerone&logoColor=ffd84d"/>
<img src="https://img.shields.io/badge/Hack_The_Box-0d1117?style=for-the-badge&logo=hackthebox&logoColor=ffd84d"/>
</p>

**Playbooks:** `PTES` · `OWASP WSTG / ASVS` · `OWASP API Top 10` · `MITRE ATT&CK` · `STRIDE`<br/>
**Training:** APIsec University track: API Security Architect, OWASP API Top 10, API Gateway Security, PCI API Security, API Security in DevSecOps

---

### `0x06` &nbsp;// telemetry

<div align="center">

<img src="https://raw.githubusercontent.com/lborakove/lborakove/output/neofetch.svg" alt="neofetch-style GitHub telemetry" width="100%"/>

<br/><br/>

<img src="https://raw.githubusercontent.com/lborakove/lborakove/output/bughunt.svg" alt="a pixel hacker hunting bugs across my contribution graph" width="100%"/>

<sub>▲ live: a pixel hacker hunts this week's bugs across my real contribution graph. regenerated every 12h by a GitHub Action.</sub>

</div>

---

### `0x07` &nbsp;// rules of engagement

```diff
+ authorized scope only. scope is law.
+ evidence over assumptions: every finding ships with a reproducible PoC
+ exploitability over CVSS theater
+ a finding without a fix is just a complaint
+ responsible disclosure, always
- no unauthorized testing. no exceptions.
```

---

### `0x08` &nbsp;// capture the flag 🏴

There's a flag hidden somewhere in this repository.

```
format : BRK{...}
hint 1 : recon is half the battle. what you see is not all that's served.
hint 2 : two layers. one of them is older than computers.
```

<sub>Found it? Open an issue titled <code>pwned</code> with <b>only the first 6 characters</b> after <code>BRK{</code>. No spoilers for the next player.</sub>

<div align="center">

<br/>

```
[ connection closed by foreign host ]
```

</div>
