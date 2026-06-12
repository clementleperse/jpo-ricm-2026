#!/usr/bin/env python3
import os
import zipfile

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "print")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ACTIVITIES = [
    # (num, name, price)
    (34, "Parcours Cdo enfant",     "1"),
    (46, "Parcours Cdo ados",       "1"),
    (47, "Tir grenade factice",     "1"),
    (72, "Course d'orientation",    "1"),
    (31, "Tir air soft",            "2"),
    (33, "Parcours OB / évasion",   "2"),
    (36, "Parcours évasion",        "2"),
    (49, "Parcours PLO",            "2"),
    (71, "Pistolet laser",          "2"),
    (41, "Parcours VBL",            "3"),
    (51, "Challenge VBS",           "3"),
]

def split_name(name):
    """Split long names across two lines at slash or space mid-point."""
    if "/" in name:
        parts = name.split("/")
        return parts[0].strip() + "<br>" + parts[1].strip()
    words = name.split()
    if len(words) >= 3:
        mid = len(words) // 2
        return " ".join(words[:mid]) + "<br>" + " ".join(words[mid:])
    return name

def make_html(num, name, price):
    display_name = split_name(name)
    slug = f"{num:02d}-{name.lower().replace(' ', '-').replace('/', '').replace(chr(39), '')}"
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Affiche {num} — {name}</title>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --green:   #2D4A2D;
    --green-d: #1F3520;
    --sand:    #C8B89A;
    --sand-bg: #F6F2EA;
    --red:     #C8102E;
    --white:   #FFFFFF;
    --ink:     #1C211C;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html, body {{
    width: 210mm;
    height: 297mm;
    background: #fff;
  }}

  /* Screen preview centering */
  @media screen {{
    body {{
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: #1a1a1a;
    }}
  }}

  .page {{
    width: 210mm;
    height: 297mm;
    position: relative;
    overflow: hidden;
    background: var(--white);
    font-family: 'Barlow', sans-serif;
  }}

  @media print {{
    html, body {{ margin: 0; padding: 0; background: #fff; }}
    .page {{ box-shadow: none; }}
    @page {{ size: A4; margin: 0; }}
  }}

  /* ── DIAGONAL GREEN TOP ── */
  .diagonal-bg {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 148mm;
    background: var(--green);
    clip-path: polygon(0 0, 100% 0, 100% 62%, 0 100%);
    z-index: 0;
  }}

  /* ── ACTIVITY NUMBER ── */
  .num-badge {{
    position: absolute;
    top: 9mm; left: 10mm;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 7px;
  }}
  .num-label {{
    font-family: 'Oswald', sans-serif;
    font-size: 11px;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: var(--sand);
    opacity: .65;
  }}
  .num-value {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: var(--sand);
    background: rgba(200,184,154,.15);
    border: 1px solid rgba(200,184,154,.35);
    border-radius: 3px;
    padding: 2px 9px;
    letter-spacing: .05em;
  }}

  /* ── ACTIVITY NAME ── */
  .activite-section {{
    position: relative; z-index: 2;
    padding-top: 42mm;
    text-align: center;
    padding-left: 14mm;
    padding-right: 14mm;
  }}
  .activite-nom {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 62px;
    line-height: .95;
    color: var(--white);
    text-transform: uppercase;
    letter-spacing: .02em;
    margin-bottom: 5mm;
  }}
  .activite-sous {{
    font-family: 'Barlow', sans-serif;
    font-size: 13px;
    color: rgba(255,255,255,.5);
    letter-spacing: .14em;
    text-transform: uppercase;
  }}

  /* ── PRICE CARD ── */
  .prix-section {{
    position: relative; z-index: 2;
    margin-top: 18mm;
    text-align: center;
  }}
  .prix-card {{
    display: inline-block;
    background: var(--white);
    border-radius: 5px;
    box-shadow: 0 8px 40px rgba(0,0,0,.18);
    padding: 10mm 22mm 9mm;
    border-top: 5px solid var(--red);
  }}
  .prix-eyebrow {{
    font-family: 'Barlow', sans-serif;
    font-size: 10px;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--red);
    margin-bottom: 2mm;
  }}
  .prix-number {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 100px;
    line-height: .9;
    color: var(--ink);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 4px;
  }}
  .prix-number .currency {{
    font-size: 44px;
    margin-top: 16px;
    color: var(--green-d);
  }}
  .prix-unit {{
    font-family: 'Barlow', sans-serif;
    font-size: 11px;
    color: var(--ink);
    opacity: .4;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-top: 3mm;
  }}

  /* ── FOOTER BAND ── */
  .footer-band {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: var(--green-d);
    padding: 5mm 10mm;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 2;
  }}
  .footer-band span {{
    font-family: 'Oswald', sans-serif;
    font-size: 10px;
    letter-spacing: .18em;
    color: var(--sand);
    opacity: .65;
    text-transform: uppercase;
  }}
  .footer-dot {{
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--red);
    opacity: .8;
  }}
</style>
</head>
<body>
<div class="page">

  <div class="diagonal-bg"></div>

  <div class="num-badge">
    <span class="num-label">N°</span>
    <span class="num-value">{num}</span>
  </div>

  <div class="activite-section">
    <div class="activite-nom">{display_name}</div>
    <div class="activite-sous">Activité proposée par le RICM</div>
  </div>

  <div class="prix-section">
    <div class="prix-card">
      <div class="prix-eyebrow">Tarif participation</div>
      <div class="prix-number">
        {price}<span class="currency">€</span>
      </div>
      <div class="prix-unit">par personne</div>
    </div>
  </div>

  <div class="footer-band">
    <span>RICM</span>
    <div class="footer-dot"></div>
    <span>Journée Portes Ouvertes</span>
    <div class="footer-dot"></div>
    <span>2026</span>
  </div>

</div>
</body>
</html>"""

# Generate all files
files = []
for num, name, price in ACTIVITIES:
    safe = name.lower().replace(" ", "-").replace("/", "").replace("'", "").replace("é","e").replace("è","e").replace("à","a")
    filename = f"{num:02d}_{safe}_{price}eur.html"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(make_html(num, name, price))
    files.append(path)
    print(f"  ✓ {filename}")

# Create zip
zip_path = os.path.join(os.path.dirname(__file__), "affiches-tarif-jpo2026.zip")
with zipfile.ZipFile(zip_path, "w") as zf:
    for p in files:
        zf.write(p, os.path.basename(p))

print(f"\n✓ ZIP créé : {zip_path}")
print(f"✓ {len(files)} affiches générées")
