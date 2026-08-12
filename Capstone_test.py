"""


FEATURES:
  1.  Real anatomical organ shapes (SVG-accurate paths)
  2.  Full GI digestion animation (mouth→stomach→intestines→colon)
  3.  Peristalsis wave animation along gut tract
  4.  Nutrient absorption panel (what absorbs where)
  5.  Toxin clearance timers for harmful compounds
  6.  28-nutrient RDA tracker with progress bars
  7.  Real-time macro breakdown (carbs/protein/fat/fiber)
  8.  Blood glucose curve simulation (GI-based)
  9.  Systemic inflammation heatmap overlay
  10. Gut microbiome diversity meter
  11. Circadian eating panel (food effects vary by time of day)
  12. Liver detox queue with compound clearance times
  13. Heart rate variability stress indicator
  14. Neurotransmitter gauge (dopamine/serotonin/cortisol/GABA)
  15. Bone mineral density tracker
  16. Hormonal disruption panel (insulin/leptin/ghrelin/cortisol)
  17. 7-day diet history with trajectory sparkline
  18. Organ speech bubbles (organs "speak" when stressed)
  19. Supplement deficiency detector & recommendations
  20. Sleep quality predictor
  21. 5 body system meters (energy/gut/inflammation/brain/heart)
  22. Animated food particle travel along body path
  23. Per-organ health score with mini health bar
  24. Comprehensive food hover tooltip with nutritional profile
  25. Draggable food cards with nutrient badge pills
  26. Effect log with scrollable history
  27. Drop-zone pulse hints when dragging
  28. Full help overlay
  29. Reset / full session clear
  30. Antioxidant ORAC score tracker
  31. Omega-3 : Omega-6 ratio gauge
  32. Glycemic load accumulator
  33. Telomere aging stress indicator
  34. Detox/liver load queue visualization
  35. BMI-neutral cellular health score



Controls:
  Drag food card → body     Feed the body
  Hover food card           Full nutritional profile
  Tab / 1-6                 Switch view panels
  H                         Help overlay
  R                         Full reset
  T                         Toggle time of day (circadian)
  Q / Escape                Quit
"""

import pygame, sys, math, random, textwrap, time, colorsys
pygame.init()

# ═══════════════════════════════════════════════════════════════
#  SCALE HELPERS  — must come before window, fonts, and layout
#  Reference design was 1600x920. Everything scales from there.
# ═══════════════════════════════════════════════════════════════
_info = pygame.display.Info()
# 95% width, 92% height so the taskbar stays visible
W = max(1024, int(_info.current_w * 0.95))
H = max(680,  int(_info.current_h * 0.92))

_SX = W / 1600.0   # horizontal scale factor
_SY = H / 920.0    # vertical scale factor
_S  = min(_SX, _SY)  # uniform scale for fonts & square elements

def sx(v): return max(1, int(v * _SX))   # scale horizontal pixels
def sy(v): return max(1, int(v * _SY))   # scale vertical pixels
def ss(v): return max(1, int(v * _S))    # scale fonts / radii uniformly

# ═══════════════════════════════════════════════════════════════
#  WINDOW
# ═══════════════════════════════════════════════════════════════
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Human Body Nutrition Simulator — Master Edition")
clock = pygame.time.Clock()

# ═══════════════════════════════════════════════════════════════
#  FONTS  — use ss() so they scale with the screen
# ═══════════════════════════════════════════════════════════════
def mf(size, bold=False): return pygame.font.SysFont("segoeui", ss(size), bold=bold)

FT   = mf(19, True);  FB   = mf(14);      FS   = mf(12)
FSS  = mf(10);        FH   = mf(26, True); FORD = mf(11, True)
FBD  = mf(13, True);  FCARD= mf(12, True); FNUM = mf(20, True)
FSML = mf(18, True);  FTAB = mf(13, True); FMIC = mf(9)
FICON_SM=mf(16); FICON_MD=mf(22); FICON_LG=mf(26); FICON_XL=mf(28)

# ═══════════════════════════════════════════════════════════════
#  COLOURS
# ═══════════════════════════════════════════════════════════════
BG        = (8,  10, 20)
PANEL_L   = (14, 17, 34)
PANEL_R   = (11, 13, 28)
PANEL_BOT = (10, 12, 24)
DIVIDER   = (32, 38, 65)
BODY_FILL = (32, 44, 82)
BODY_EDGE = (65, 95, 160)
WHITE     = (238, 243, 255)
GREY      = (105, 115, 150)
LGREY     = (155, 165, 195)
GOLD      = (255, 200, 50)
TRAD      = (50, 185, 105)
MOD       = (225, 80, 50)
GOOD      = (55, 215, 125)
BAD       = (255, 70, 70)
NEUTRAL   = (135, 145, 175)
ACCENT    = (100, 160, 255)
WARN      = (255, 175, 40)
GUT_COL   = (120, 200, 120)
BLOOD_COL = (200, 60, 80)
NEURO_COL = (140, 100, 220)

METER_COLS = {
    "Energy":         (255, 195, 45),
    "Gut Health":     (75, 195, 115),
    "Inflammation":   (215, 88, 58),
    "Brain Clarity":  (95, 165, 250),
    "Heart Strength": (215, 75, 105),
}

# ═══════════════════════════════════════════════════════════════
#  LAYOUT  — all values scale with screen size
# ═══════════════════════════════════════════════════════════════
LEFT_W   = sx(240)   # food panel
RIGHT_W  = sx(290)   # HUD / tabs panel
BOT_H    = sy(200)   # bottom digestion panel
BODY_CX  = LEFT_W + (W - LEFT_W - RIGHT_W) // 2
BODY_TOP = sy(60)
TAB_H    = sy(34)
CARD_W   = sx(108)
CARD_H   = sy(65)

# ═══════════════════════════════════════════════════════════════
#  REAL ORGAN SHAPES  (SVG-accurate pygame draw paths)
#  Each organ = list of drawing commands executed relative to (cx, cy)
#  Format: ("ellipse", rx, ry)  or  ("path", [(x,y)...], closed)
#  All coordinates are relative offsets from the organ world position
# ═══════════════════════════════════════════════════════════════
ORGANS = {
    "Brain": {
        "rel": (0, 15), "col": (110, 90, 210),
        "desc": "Cognition, mood, neurotransmitters",
        # Draw as two overlapping lobes + cerebellum
        "shape": [
            ("ellipse_off", -10, 0, 36, 30),   # left lobe
            ("ellipse_off",  10, 0, 36, 30),   # right lobe
            ("ellipse_off",   0, 24, 22, 12),  # cerebellum
        ],
        "hit_rx": 42, "hit_ry": 35,
    },
    "Heart": {
        "rel": (-30, 148), "col": (215, 60, 80),
        "desc": "Pumps blood, cardiovascular control",
        "shape": [
            ("heart", 0, 0, 28),   # heart shape
        ],
        "hit_rx": 30, "hit_ry": 32,
    },
    "Lungs": {
        "rel": (30, 152), "col": (170, 110, 90),
        "desc": "Gas exchange, inflammation response",
        "shape": [
            ("lung_l", -22, 0, 22, 40),  # left lung lobe
            ("lung_r",  22, 0, 22, 40),  # right lung lobe
        ],
        "hit_rx": 54, "hit_ry": 42,
    },
    "Liver": {
        "rel": (26, 210), "col": (150, 92, 52),
        "desc": "Detox, fat metabolism, bile",
        "shape": [
            ("liver", 0, 0, 42, 26),  # irregular wedge
        ],
        "hit_rx": 40, "hit_ry": 28,
    },
    "Gut": {
        "rel": (0, 276), "col": (90, 160, 90),
        "desc": "Microbiome, absorption, immunity",
        "shape": [
            ("gut_coil", 0, 0, 44, 46),  # coiled intestine shape
        ],
        "hit_rx": 46, "hit_ry": 50,
    },
    "Skin": {
        "rel": (0, 385), "col": (192, 150, 110),
        "desc": "Barrier, collagen, inflammation",
        "shape": [
            ("ellipse_off", 0, 0, 64, 18),
        ],
        "hit_rx": 65, "hit_ry": 22,
    },
}

def draw_organ_shape(surf, name, cx, cy, col, edge_col, alpha_surf=None):
    """Draw anatomically-inspired organ shape."""
    target = surf if alpha_surf is None else alpha_surf
    o = ORGANS[name]
    for cmd in o["shape"]:
        kind = cmd[0]
        if kind == "ellipse_off":
            _, ox, oy, rx, ry = cmd
            pygame.draw.ellipse(target, col,
                (cx+ox-rx, cy+oy-ry, rx*2, ry*2))
            pygame.draw.ellipse(target, edge_col,
                (cx+ox-rx, cy+oy-ry, rx*2, ry*2), 2)

        elif kind == "heart":
            _, ox, oy, size = cmd
            s = size
            pts = []
            for i in range(60):
                t = math.pi * 2 * i / 60
                x = s * (16*math.sin(t)**3) / 16
                y = -s * (13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t)) / 16
                pts.append((int(cx+ox+x), int(cy+oy+y)))
            if len(pts) >= 3:
                pygame.draw.polygon(target, col, pts)
                pygame.draw.polygon(target, edge_col, pts, 2)

        elif kind in ("lung_l", "lung_r"):
            _, ox, oy, rw, rh = cmd
            # Draw lung as rounded trapezoid
            sign = -1 if kind == "lung_l" else 1
            pts = [
                (cx+ox + sign*4,  cy+oy-rh),
                (cx+ox + sign*rw, cy+oy-rh//2),
                (cx+ox + sign*rw, cy+oy+rh//2),
                (cx+ox + sign*4,  cy+oy+rh),
                (cx+ox,           cy+oy+rh//2),
                (cx+ox,           cy+oy-rh//2),
            ]
            if len(pts) >= 3:
                pygame.draw.polygon(target, col, pts)
                pygame.draw.polygon(target, edge_col, pts, 2)
            # Bronchi
            pygame.draw.line(target, edge_col,
                (cx+ox, cy+oy-rh//2), (cx+ox+sign*rw//2, cy+oy), 2)
            pygame.draw.line(target, edge_col,
                (cx+ox+sign*rw//2, cy+oy),
                (cx+ox+sign*rw//3, cy+oy+rh//3), 1)

        elif kind == "liver":
            _, ox, oy, rw, rh = cmd
            pts = [
                (cx+ox-rw,     cy+oy-rh//2),
                (cx+ox+rw//2,  cy+oy-rh),
                (cx+ox+rw,     cy+oy),
                (cx+ox+rw//2,  cy+oy+rh),
                (cx+ox-rw//2,  cy+oy+rh//2),
            ]
            if len(pts) >= 3:
                pygame.draw.polygon(target, col, pts)
                pygame.draw.polygon(target, edge_col, pts, 2)

        elif kind == "gut_coil":
            _, ox, oy, rw, rh = cmd
            # Draw as several concentric arcs suggesting intestinal loops
            for ring in range(3):
                r_off = ring * 12
                erect = pygame.Rect(
                    cx+ox-rw+r_off, cy+oy-rh+r_off,
                    (rw-r_off)*2,   (rh-r_off)*2)
                if erect.width > 4 and erect.height > 4:
                    pygame.draw.ellipse(target, col, erect)
                    pygame.draw.ellipse(target, edge_col, erect, 1)


# ═══════════════════════════════════════════════════════════════
#  BADGE DEFINITIONS
# ═══════════════════════════════════════════════════════════════
BADGE_DEFS = {
    "fiber":    ("Fiber",     (55, 180, 95)),
    "omega3":   ("Omega-3",   (55, 135, 215)),
    "antioxid": ("Antioxid.", (175, 75, 205)),
    "sugar":    ("Sugar",     (215, 165, 35)),
    "sat_fat":  ("Sat.Fat",   (210, 75, 55)),
    "sodium":   ("Sodium",    (195, 125, 45)),
    "protein":  ("Protein",   (95, 165, 215)),
    "probiotic":("Probiotic", (75, 205, 155)),
    "caffeine": ("Caffeine",  (195, 135, 55)),
    "nitrates": ("Nitrates",  (195, 55, 75)),
    "transfat": ("Trans Fat", (215, 45, 45)),
    "polyphen": ("Polyphen.", (125, 75, 195)),
    "vitd":     ("Vit.D",     (235, 205, 75)),
    "magnes":   ("Magnesium", (75, 185, 175)),
    "curcumin": ("Curcumin",  (225, 165, 35)),
    "fructose": ("Fructose",  (215, 75, 75)),
    "calcium":  ("Calcium",   (200, 200, 100)),
    "zinc":     ("Zinc",      (120, 155, 195)),
    "vitc":     ("Vit.C",     (235, 155, 45)),
    "folate":   ("Folate",    (100, 190, 130)),
}

# ═══════════════════════════════════════════════════════════════
#  GI TRACT WAYPOINTS  (body-relative coordinates for digestion animation)
#  The food bolus travels through these points sequentially
# ═══════════════════════════════════════════════════════════════
def gi_waypoints():
    cx = BODY_CX
    top = BODY_TOP
    return [
        (cx,       top + 78),   # 0  mouth/throat
        (cx,       top + 98),   # 1  esophagus top
        (cx,       top + 140),  # 2  esophagus bottom
        (cx,       top + 175),  # 3  stomach entry (cardia)
        (cx - 20,  top + 210),  # 4  stomach body
        (cx + 5,   top + 235),  # 5  stomach exit (pylorus)
        (cx + 20,  top + 260),  # 6  duodenum
        (cx + 35,  top + 285),  # 7  jejunum
        (cx + 10,  top + 305),  # 8  ileum
        (cx - 20,  top + 320),  # 9  ileocecal junction
        (cx - 40,  top + 310),  # 10 cecum / ascending colon
        (cx - 45,  top + 270),  # 11 ascending colon
        (cx - 30,  top + 255),  # 12 hepatic flexure
        (cx + 20,  top + 255),  # 13 transverse colon
        (cx + 40,  top + 270),  # 14 splenic flexure
        (cx + 45,  top + 310),  # 15 descending colon
        (cx + 30,  top + 350),  # 16 sigmoid colon
        (cx,       top + 360),  # 17 rectum
    ]

GI_STAGE_LABELS = [
    "Mouth", "Throat", "Esophagus", "Cardia",
    "Stomach", "Pylorus", "Duodenum", "Jejunum",
    "Ileum", "Ileocecal", "Cecum", "Ascending colon",
    "Hepatic flex.", "Transverse colon", "Splenic flex.",
    "Descending colon", "Sigmoid", "Rectum"
]

GI_STAGE_ABSORPTION = {
    4:  "Protein denaturation begins (pH 1.5-3.5)",
    5:  "Chyme formation complete",
    6:  "Bile emulsifies fats; pancreatic enzymes activate",
    7:  "80% of nutrients absorbed here",
    8:  "B12, bile salts, remaining nutrients absorbed",
    9:  "Water & electrolytes absorbed",
    12: "Short-chain fatty acids from fiber fermentation",
    16: "Final water absorption; waste compacted",
}

# ═══════════════════════════════════════════════════════════════
#  HARMFUL COMPOUNDS with clearance times
# ═══════════════════════════════════════════════════════════════
HARMFUL_COMPOUNDS = {
    # compound_key: (display_name, clearance_hours, color, foods_that_contain)
    "acrylamide":   ("Acrylamide",     72,  (220, 80,  60),  ["Potato Chips", "White Bread"]),
    "nitrosamines": ("Nitrosamines",   48,  (200, 60,  80),  ["Hot Dog"]),
    "trans_fat":    ("Trans fat",      96,  (220, 50,  50),  ["Burger + Fries", "Potato Chips"]),
    "fructose_met": ("Fructose metabolites", 24, (215, 160, 40), ["Cola / Soda", "Candy", "Ice Cream"]),
    "caffeine":     ("Caffeine",        6,  (195, 135, 55),  ["Energy Drink"]),
    "sodium_load":  ("Sodium excess",  18,  (195, 120, 45),  ["Burger + Fries", "Potato Chips", "Hot Dog"]),
    "artificial_sw":("Artificial sweeteners", 12, (170, 100, 200), ["Cola / Soda"]),
    "sat_fat_lipid":("Oxidised LDL",   36,  (215, 75,  55),  ["Burger + Fries", "Ice Cream", "Hot Dog"]),
    "agEs":         ("Glycation (AGEs)", 30, (220, 150, 40), ["Candy", "White Bread", "Ice Cream"]),
    "phosphoric":   ("Phosphoric acid",  8,  (150, 180, 100), ["Cola / Soda"]),
}

# ═══════════════════════════════════════════════════════════════
#  28-NUTRIENT RDA TRACKER
# ═══════════════════════════════════════════════════════════════
RDA_NUTRIENTS = [
    # (key, display, rda_unit, col)
    ("vitA",   "Vitamin A",    "900 mcg",  (255, 150, 50)),
    ("vitB1",  "Vitamin B1",   "1.2 mg",   (255, 200, 80)),
    ("vitB2",  "Vitamin B2",   "1.3 mg",   (255, 210, 90)),
    ("vitB3",  "Vitamin B3",   "16 mg",    (255, 185, 60)),
    ("vitB6",  "Vitamin B6",   "1.7 mg",   (255, 175, 55)),
    ("vitB12", "Vitamin B12",  "2.4 mcg",  (100, 200, 255)),
    ("vitC",   "Vitamin C",    "90 mg",    (255, 180, 50)),
    ("vitD",   "Vitamin D",    "20 mcg",   (235, 210, 80)),
    ("vitE",   "Vitamin E",    "15 mg",    (200, 220, 80)),
    ("vitK",   "Vitamin K",    "120 mcg",  (120, 210, 100)),
    ("folate", "Folate",       "400 mcg",  (100, 195, 130)),
    ("calcium","Calcium",      "1000 mg",  (200, 200, 100)),
    ("iron",   "Iron",         "18 mg",    (200, 100, 80)),
    ("magnes", "Magnesium",    "420 mg",   (80, 190, 175)),
    ("zinc",   "Zinc",         "11 mg",    (120, 155, 200)),
    ("potass", "Potassium",    "4700 mg",  (170, 150, 220)),
    ("sodium", "Sodium",       "2300 mg",  (195, 130, 50)),
    ("phosph", "Phosphorus",   "700 mg",   (150, 185, 100)),
    ("selen",  "Selenium",     "55 mcg",   (100, 190, 170)),
    ("copper", "Copper",       "0.9 mg",   (185, 130, 60)),
    ("omega3", "Omega-3",      "1.6 g",    (60, 140, 220)),
    ("omega6", "Omega-6",      "17 g",     (220, 140, 60)),
    ("fiber",  "Fiber",        "38 g",     (60, 185, 100)),
    ("protein","Protein",      "56 g",     (100, 170, 220)),
    ("carbs",  "Carbohydrates","130 g",    (220, 180, 60)),
    ("fat",    "Total fat",    "78 g",     (215, 130, 50)),
    ("water",  "Water",        "3.7 L",    (80, 170, 230)),
    ("choline","Choline",      "550 mg",   (160, 100, 200)),
]

# ═══════════════════════════════════════════════════════════════
#  FOOD DATABASE  (comprehensive)
# ═══════════════════════════════════════════════════════════════
FOODS = [
    # TRADITIONAL FOODS
    {
        "name": "Brown Rice", "kind": "trad", "icon": "\U0001f33e",
        "badges": ["fiber", "magnes"],
        "profile": "Whole grain with intact bran layer. Rich in magnesium, B vitamins, and resistant starch (GI ~55). Feeds Bifidobacterium via fermentation.",
        "system": {"Energy":+4,"Gut Health":+5,"Inflammation":-3,"Brain Clarity":+3},
        "organs": {
            "Gut":  (True, "+Prebiotic starch", "Resistant starch ferments → butyrate → colonocyte fuel → tighter gut lining."),
            "Heart":(True, "+Steady insulin",   "Low GI prevents hyperinsulinemia, a key CVD driver."),
            "Brain":(True, "+B vitamins",       "Thiamine & B6 essential for serotonin/dopamine synthesis."),
        },
        "nutrients_added": {"fiber":4,"magnes":15,"vitB1":10,"vitB3":15,"carbs":35,"protein":5},
        "harmful_compounds": {},
        "gi_index": 55, "macros": {"carbs":46,"protein":5,"fat":2,"fiber":3.5},
        "microbiome": {"Bifidobacterium":+8,"Lactobacillus":+4,"Faecalibacterium":+3},
        "orac": 180,
        "hormone_effect": {"insulin":+15,"cortisol":0,"leptin":+5,"ghrelin":-8},
        "circadian": {"morning":1.2,"afternoon":1.0,"evening":0.8},
        "sleep_effect": +1,
    },
    {
        "name": "Wild Salmon", "kind": "trad", "icon": "\U0001f41f",
        "badges": ["omega3","protein","vitd"],
        "profile": "Exceptional EPA & DHA source. Wild-caught has 3-4x more omega-3 than farmed. Contains astaxanthin and vitamin D3. Potent anti-inflammatory.",
        "system": {"Energy":+3,"Gut Health":+2,"Inflammation":-7,"Brain Clarity":+7,"Heart Strength":+6},
        "organs": {
            "Brain":(True, "+DHA structural fat",  "DHA = 30% of brain grey matter. Critical for synaptic membranes."),
            "Heart":(True, "+EPA, lower TG",       "EPA lowers triglycerides ~30%, reduces platelet aggregation."),
            "Lungs":(True, "+Omega-3 barrier",     "Reduces leukotriene synthesis in airways; improves FEV1 in asthma."),
            "Skin": (True, "+Lipid bilayer",       "DHA maintains skin cell membrane integrity, reduces TEWL."),
        },
        "nutrients_added": {"omega3":85,"vitD":80,"protein":60,"vitB12":70,"selen":50,"phosph":35},
        "harmful_compounds": {},
        "gi_index": 0, "macros": {"carbs":0,"protein":25,"fat":12,"fiber":0},
        "microbiome": {"Lactobacillus":+5,"Bifidobacterium":+3},
        "orac": 520,
        "hormone_effect": {"insulin":+3,"cortisol":-8,"leptin":+4,"ghrelin":-10},
        "circadian": {"morning":1.1,"afternoon":1.3,"evening":1.2},
        "sleep_effect": +3,
    },
    {
        "name": "Blueberries", "kind": "trad", "icon": "\U0001fad0",
        "badges": ["antioxid","polyphen","fiber"],
        "profile": "ORAC 4669/100g. Anthocyanins cross blood-brain barrier. Pterostilbene & resveratrol improve arterial flexibility. Low sugar (14g/100g).",
        "system": {"Energy":+2,"Inflammation":-6,"Brain Clarity":+6,"Heart Strength":+4},
        "organs": {
            "Brain":(True, "+BDNF activation",   "Anthocyanins activate BDNF, promoting hippocampal neurogenesis."),
            "Heart":(True, "+Arterial flex",     "Lowers systolic BP 4-6 mmHg, improves endothelial NO production."),
            "Skin": (True, "+UV defence",        "Polyphenols upregulate Nrf2 antioxidant pathway in skin cells."),
        },
        "nutrients_added": {"vitC":20,"fiber":5,"vitK":12,"folate":4,"manganese":20},
        "harmful_compounds": {},
        "gi_index": 53, "macros": {"carbs":14,"protein":1,"fat":0.5,"fiber":2.4},
        "microbiome": {"Bifidobacterium":+10,"Akkermansia":+8,"Lactobacillus":+5},
        "orac": 4669,
        "hormone_effect": {"insulin":+8,"cortisol":-5,"leptin":+3,"ghrelin":-5},
        "circadian": {"morning":1.4,"afternoon":1.2,"evening":0.9},
        "sleep_effect": +2,
    },
    {
        "name": "Lentils", "kind": "trad", "icon": "\U0001fad8",
        "badges": ["fiber","protein","magnes"],
        "profile": "18g protein + 15g fiber/cup. GI ~21. Fermentable fiber dramatically increases microbiome diversity. Rich in folate for liver methylation.",
        "system": {"Energy":+3,"Gut Health":+8,"Inflammation":-4,"Heart Strength":+4},
        "organs": {
            "Gut":  (True, "+Microbiome diversity","Fermentable fiber is the #1 driver of microbiome diversity."),
            "Heart":(True, "+LDL reduction",       "Soluble fiber binds bile acids → liver pulls LDL from blood."),
            "Liver":(True, "+Folate methylation",  "Folate essential for phase 2 liver detox (methylation pathway)."),
        },
        "nutrients_added": {"fiber":12,"protein":30,"folate":45,"iron":25,"magnes":18,"potass":20},
        "harmful_compounds": {},
        "gi_index": 21, "macros": {"carbs":40,"protein":18,"fat":1,"fiber":15},
        "microbiome": {"Bifidobacterium":+12,"Faecalibacterium":+10,"Roseburia":+8},
        "orac": 340,
        "hormone_effect": {"insulin":+10,"cortisol":0,"leptin":+8,"ghrelin":-15},
        "circadian": {"morning":1.0,"afternoon":1.2,"evening":1.1},
        "sleep_effect": +1,
    },
    {
        "name": "Olive Oil", "kind": "trad", "icon": "\U0001fad2",
        "badges": ["polyphen","omega3"],
        "profile": "EVOO oleocanthal = natural COX inhibitor (same mechanism as ibuprofen). 73% oleic acid. PREDIMED trial: 30% CVD reduction. 30+ phenolic compounds.",
        "system": {"Energy":+2,"Inflammation":-6,"Brain Clarity":+4,"Heart Strength":+5},
        "organs": {
            "Heart":(True, "+Anti-atherosclerotic","Oleic acid reduces LDL oxidation; phenols increase HDL."),
            "Brain":(True, "+Myelin support",      "Monounsaturated fats maintain axonal myelin sheath integrity."),
            "Liver":(True, "+Hepatoprotective",    "Oleocanthal reduces hepatic fat and lowers ALT/AST enzymes."),
        },
        "nutrients_added": {"omega3":5,"vitE":40,"vitK":8,"polyphenols":30},
        "harmful_compounds": {},
        "gi_index": 0, "macros": {"carbs":0,"protein":0,"fat":14,"fiber":0},
        "microbiome": {"Lactobacillus":+4,"Bifidobacterium":+3},
        "orac": 310,
        "hormone_effect": {"insulin":+2,"cortisol":-4,"leptin":+2,"ghrelin":-3},
        "circadian": {"morning":1.0,"afternoon":1.2,"evening":1.1},
        "sleep_effect": +1,
    },
    {
        "name": "Turmeric", "kind": "trad", "icon": "\U0001f33f",
        "badges": ["curcumin","antioxid"],
        "profile": "Curcumin inhibits NF-kB (master inflammation switch). +2000% bioavailability with piperine. Crosses blood-brain barrier. Reduces amyloid plaques.",
        "system": {"Energy":+1,"Gut Health":+4,"Inflammation":-8,"Brain Clarity":+4},
        "organs": {
            "Brain":(True, "+Curcumin neuroprotection","Reduces beta-amyloid, increases BDNF, potential Alzheimer's prevention."),
            "Gut":  (True, "+Tight junctions",         "Strengthens intestinal tight junction proteins, reduces permeability."),
            "Liver":(True, "+Phase 2 detox",            "Upregulates glutathione-S-transferase for toxin conjugation."),
            "Lungs":(True, "+Cytokine inhibition",      "Downregulates IL-1b, IL-6, TNF-alpha in lung tissue."),
        },
        "nutrients_added": {"curcumin":50,"iron":8,"vitC":3,"fiber":2},
        "harmful_compounds": {},
        "gi_index": 0, "macros": {"carbs":5,"protein":1,"fat":1,"fiber":2},
        "microbiome": {"Lactobacillus":+8,"Bifidobacterium":+6,"Faecalibacterium":+5},
        "orac": 1270,
        "hormone_effect": {"insulin":0,"cortisol":-6,"leptin":+1,"ghrelin":-2},
        "circadian": {"morning":1.3,"afternoon":1.1,"evening":1.0},
        "sleep_effect": +2,
    },
    {
        "name": "Walnuts", "kind": "trad", "icon": "\U0001f95c",
        "badges": ["omega3","polyphen","magnes"],
        "profile": "Only nut with ALA omega-3 (2.5g/oz). Ellagitannins → urolithins via gut bacteria → mitophagy activation. 26% lower cognitive impairment odds.",
        "system": {"Energy":+2,"Gut Health":+4,"Inflammation":-5,"Brain Clarity":+5,"Heart Strength":+4},
        "organs": {
            "Brain":(True, "+ALA/DHA precursor",  "ALA converts to DHA in brain. 26% lower cognitive impairment odds."),
            "Heart":(True, "+Endothelial function","Walnuts improve flow-mediated dilation within 4 hours of consumption."),
            "Gut":  (True, "+Urolithin synthesis", "Gut bacteria convert ellagitannins → urolithins → mitophagy."),
        },
        "nutrients_added": {"omega3":45,"magnes":12,"vitB6":10,"folate":6,"fiber":4,"vitE":5},
        "harmful_compounds": {},
        "gi_index": 15, "macros": {"carbs":14,"protein":15,"fat":65,"fiber":7},
        "microbiome": {"Bifidobacterium":+7,"Lactobacillus":+5,"Akkermansia":+5},
        "orac": 1350,
        "hormone_effect": {"insulin":+5,"cortisol":-3,"leptin":+6,"ghrelin":-8},
        "circadian": {"morning":1.1,"afternoon":1.2,"evening":0.9},
        "sleep_effect": +2,
    },
    {
        "name": "Kefir", "kind": "trad", "icon": "\U0001f95b",
        "badges": ["probiotic","protein","vitd"],
        "profile": "30+ live bacterial and yeast strains. Up to 10 billion CFU/serving. Vitamin K2 routes calcium to bones not arteries. Clinically reduces IBS and C.diff.",
        "system": {"Energy":+2,"Gut Health":+9,"Inflammation":-4,"Brain Clarity":+3},
        "organs": {
            "Gut":  (True, "+30-strain probiotic",  "Most diverse whole-food probiotic; clinically reduces IBS and C. difficile."),
            "Brain":(True, "+Gut-brain serotonin",  "Probiotic strains produce GABA precursors; 90% of serotonin made in gut."),
            "Heart":(True, "+Vitamin K2",            "K2 activates matrix GLA protein, prevents vascular calcium deposition."),
        },
        "nutrients_added": {"protein":20,"vitD":15,"calcium":20,"vitB12":25,"probiotic_cfu":100},
        "harmful_compounds": {},
        "gi_index": 35, "macros": {"carbs":8,"protein":11,"fat":4,"fiber":0},
        "microbiome": {"Lactobacillus":+15,"Bifidobacterium":+12,"Saccharomyces":+8,"Leuconostoc":+6},
        "orac": 85,
        "hormone_effect": {"insulin":+12,"cortisol":-5,"leptin":+4,"ghrelin":-8},
        "circadian": {"morning":1.4,"afternoon":1.0,"evening":0.8},
        "sleep_effect": +3,
    },
    {
        "name": "Broccoli", "kind": "trad", "icon": "\U0001f966",
        "badges": ["vitc","fiber","folate"],
        "profile": "Sulforaphane (from glucoraphanin) is the most potent natural Nrf2 activator known. Indole-3-carbinol supports estrogen detox. 89 mg vitamin C per 100g.",
        "system": {"Energy":+2,"Gut Health":+5,"Inflammation":-5,"Brain Clarity":+3},
        "organs": {
            "Liver":(True, "+Sulforaphane",     "Sulforaphane is the #1 natural inducer of Phase 2 detox enzymes."),
            "Brain":(True, "+Vitamin K cognition","Vitamin K linked to better verbal episodic memory in adults."),
            "Gut":  (True, "+Glucosinolates",   "Glucosinolates selectively feed beneficial bacteria strains."),
            "Lungs":(True, "+Isothiocyanates",  "Reduce lung inflammation via Nrf2 pathway; protective in smokers."),
        },
        "nutrients_added": {"vitC":90,"vitK":90,"folate":14,"fiber":5,"vitB6":10,"potass":12,"calcium":5},
        "harmful_compounds": {},
        "gi_index": 10, "macros": {"carbs":7,"protein":3,"fat":0.5,"fiber":3},
        "microbiome": {"Bifidobacterium":+6,"Roseburia":+5,"Lactobacillus":+4},
        "orac": 890,
        "hormone_effect": {"insulin":+4,"cortisol":-4,"leptin":+3,"ghrelin":-6},
        "circadian": {"morning":1.2,"afternoon":1.3,"evening":1.0},
        "sleep_effect": +1,
    },
    {
        "name": "Greek Yogurt", "kind": "trad", "icon": "\U0001f963",
        "badges": ["protein","probiotic","calcium"],
        "profile": "Strained whey removes lactose & adds protein. 17g protein per 100g. Live cultures: S. thermophilus, L. bulgaricus. Rich in iodine and B12.",
        "system": {"Energy":+3,"Gut Health":+7,"Inflammation":-2,"Brain Clarity":+2,"Heart Strength":+2},
        "organs": {
            "Gut":  (True, "+Live cultures",  "S. thermophilus and L. bulgaricus survive GI transit and colonize."),
            "Brain":(True, "+Tyrosine",        "Tyrosine is the precursor to dopamine and norepinephrine."),
            "Heart":(True, "+Blood pressure",  "Fermented dairy consumption associated with 12% lower hypertension risk."),
        },
        "nutrients_added": {"protein":35,"calcium":18,"vitB12":22,"iodine":40,"phosph":20},
        "harmful_compounds": {},
        "gi_index": 11, "macros": {"carbs":5,"protein":17,"fat":2,"fiber":0},
        "microbiome": {"Lactobacillus":+10,"Streptococcus_therm":+8},
        "orac": 90,
        "hormone_effect": {"insulin":+18,"cortisol":-2,"leptin":+5,"ghrelin":-12},
        "circadian": {"morning":1.3,"afternoon":1.0,"evening":0.7},
        "sleep_effect": +2,
    },
    # MODERN / PROCESSED FOODS
    {
        "name": "Burger + Fries", "kind": "mod", "icon": "\U0001f354",
        "badges": ["sat_fat","sodium","transfat"],
        "profile": "900+ kcal, 40g sat fat, 1500mg+ sodium, residual trans fats. Within 2h: 24% impaired brachial artery dilation, elevated CRP, IL-6, TNF-alpha.",
        "system": {"Energy":-2,"Gut Health":-7,"Inflammation":+8,"Brain Clarity":-4,"Heart Strength":-6},
        "organs": {
            "Heart":(False,"Endothelial damage",    "A single meal impairs brachial artery dilation 24% for 4h."),
            "Liver":(False,"NASH trigger",          "Trans fats accumulate preferentially in liver, activating Kupffer cells."),
            "Gut":  (False,"Microbiome crash",      "High sat fat → Bacteroidetes dominance within 24h."),
            "Brain":(False,"Post-meal cognitive fog","Glucose spike → crash → impaired WM and reaction time 1-3h."),
        },
        "nutrients_added": {"sodium":60,"sat_fat":40,"protein":25,"carbs":50,"fat":45},
        "harmful_compounds": {"trans_fat":1,"sodium_load":1,"sat_fat_lipid":1},
        "gi_index": 72, "macros": {"carbs":80,"protein":30,"fat":45,"fiber":3},
        "microbiome": {"Bacteroidetes":+10,"Bifidobacterium":-8,"Lactobacillus":-6},
        "orac": 120,
        "hormone_effect": {"insulin":+50,"cortisol":+10,"leptin":-5,"ghrelin":+15},
        "circadian": {"morning":0.8,"afternoon":0.7,"evening":0.5},
        "sleep_effect": -4,
    },
    {
        "name": "Cola / Soda", "kind": "mod", "icon": "\U0001f964",
        "badges": ["sugar","fructose","sodium"],
        "profile": "53g sugar (HFCS) per 500ml, 0 fiber, pH 2.5 phosphoric acid. Fructose → hepatic de novo lipogenesis identical to alcohol metabolism.",
        "system": {"Energy":+1,"Gut Health":-6,"Inflammation":+7,"Brain Clarity":-3,"Heart Strength":-4},
        "organs": {
            "Liver":(False,"De novo lipogenesis",   "Fructose → triglycerides via same pathway as alcohol."),
            "Gut":  (False,"Acid erosion",          "pH 2.5 destroys acid-sensitive Lactobacillus & Bifidobacterium."),
            "Brain":(False,"Dopamine receptor loss","Ultra-sweet taste downregulates D2 receptors (same as addictive drugs)."),
            "Heart":(False,"TG+32% in 10 weeks",   "2 cans/day raises fasting triglycerides 32% over 10 weeks."),
        },
        "nutrients_added": {"sugar":53,"sodium":12},
        "harmful_compounds": {"fructose_met":1,"phosphoric":1,"artificial_sw":1},
        "gi_index": 65, "macros": {"carbs":53,"protein":0,"fat":0,"fiber":0},
        "microbiome": {"Bifidobacterium":-12,"Lactobacillus":-10,"Akkermansia":-8},
        "orac": 0,
        "hormone_effect": {"insulin":+55,"cortisol":+8,"leptin":-8,"ghrelin":+20},
        "circadian": {"morning":0.7,"afternoon":0.6,"evening":0.3},
        "sleep_effect": -5,
    },
    {
        "name": "Energy Drink", "kind": "mod", "icon": "\u26a1",
        "badges": ["caffeine","sugar","sodium"],
        "profile": "150-200mg caffeine + 30-50g sugar + taurine. Prolongs QTc interval. Dysregulates HPA axis. Raises cortisol acutely by 15-25%.",
        "system": {"Energy":+5,"Gut Health":-3,"Inflammation":+5,"Brain Clarity":-2,"Heart Strength":-5},
        "organs": {
            "Heart":(False,"QTc prolongation",    "Caffeine+taurine prolongs QTc → arrhythmia risk, esp. in adolescents."),
            "Brain":(False,"HPA axis disruption", "Chronic cortisol excess → hippocampal atrophy → memory impairment."),
            "Lungs":(False,"Pulmonary HTN",       "Caffeine vasoconstricts pulmonary vessels, raises PAP."),
            "Liver":(False,"CYP1A2 overload",     "All caffeine metabolised by CYP1A2; chronic overload = oxidative stress."),
        },
        "nutrients_added": {"caffeine":1,"sugar":35,"sodium":10},
        "harmful_compounds": {"caffeine":1,"fructose_met":1},
        "gi_index": 70, "macros": {"carbs":35,"protein":0,"fat":0,"fiber":0},
        "microbiome": {"Bifidobacterium":-6,"Lactobacillus":-4},
        "orac": 0,
        "hormone_effect": {"insulin":+40,"cortisol":+25,"leptin":-6,"ghrelin":+18},
        "circadian": {"morning":0.5,"afternoon":0.6,"evening":0.2},
        "sleep_effect": -7,
    },
    {
        "name": "Potato Chips", "kind": "mod", "icon": "\U0001f35f",
        "badges": ["sodium","sat_fat","transfat"],
        "profile": "500mg sodium/bag. Acrylamide (Group 2A carcinogen) from high-heat frying. Engineered fat/salt/crunch ratios override satiety signals (bliss point).",
        "system": {"Energy":-1,"Gut Health":-5,"Inflammation":+6,"Brain Clarity":-2,"Heart Strength":-4},
        "organs": {
            "Heart":(False,"Sodium-driven HTN",    "Each 1g excess sodium raises systolic BP ~2mmHg."),
            "Liver":(False,"Acrylamide genotoxin", "Acrylamide → glycidamide → DNA adducts in hepatocytes."),
            "Skin": (False,"Omega-6 inflammation", "High LA → arachidonic acid → PGE2 → skin inflammation."),
            "Gut":  (False,"Emulsifier gut damage","Carboxymethylcellulose erodes mucus layer within 12 weeks."),
        },
        "nutrients_added": {"sodium":50,"sat_fat":15,"carbs":55,"fat":30},
        "harmful_compounds": {"acrylamide":1,"sodium_load":1,"sat_fat_lipid":1},
        "gi_index": 75, "macros": {"carbs":55,"protein":6,"fat":35,"fiber":2},
        "microbiome": {"Bifidobacterium":-8,"Lactobacillus":-7,"Akkermansia":-5},
        "orac": 50,
        "hormone_effect": {"insulin":+35,"cortisol":+5,"leptin":-8,"ghrelin":+12},
        "circadian": {"morning":0.6,"afternoon":0.7,"evening":0.4},
        "sleep_effect": -3,
    },
    {
        "name": "Candy", "kind": "mod", "icon": "\U0001f36c",
        "badges": ["sugar","fructose"],
        "profile": "Pure refined sugar + synthetic dyes. Activates mesolimbic dopamine circuit identically to cocaine in rodent models. Zero fiber = pure glycemic spike.",
        "system": {"Energy":+3,"Gut Health":-6,"Inflammation":+6,"Brain Clarity":-4},
        "organs": {
            "Brain":(False,"Dopamine hijack",   "Repeated spikes downregulate D2 receptors → needing more for same reward."),
            "Gut":  (False,"Pathogen feeding",  "Sugar feeds Candida albicans + E. coli, outcompetes commensals."),
            "Skin": (False,"Collagen glycation","Glucose + collagen → AGEs → skin stiffness + accelerated aging."),
            "Liver":(False,"Fructose lipogenesis","HFCS → hepatic TG synthesis identical to alcohol metabolism."),
        },
        "nutrients_added": {"sugar":60,"carbs":60},
        "harmful_compounds": {"fructose_met":1,"agEs":1},
        "gi_index": 78, "macros": {"carbs":65,"protein":0,"fat":0,"fiber":0},
        "microbiome": {"Candida":+15,"Bifidobacterium":-14,"Lactobacillus":-12,"Faecalibacterium":-8},
        "orac": 0,
        "hormone_effect": {"insulin":+60,"cortisol":+12,"leptin":-10,"ghrelin":+25},
        "circadian": {"morning":0.5,"afternoon":0.6,"evening":0.3},
        "sleep_effect": -6,
    },
    {
        "name": "Hot Dog", "kind": "mod", "icon": "\U0001f32d",
        "badges": ["nitrates","sodium","sat_fat"],
        "profile": "WHO Group 1 carcinogen. Sodium nitrite → N-nitrosamines. 18% higher colorectal cancer risk per 50g/day. 900mg sodium. Mechanically separated meat.",
        "system": {"Energy":-1,"Gut Health":-7,"Inflammation":+7,"Heart Strength":-5},
        "organs": {
            "Gut":  (False,"WHO Group 1 carcinogen","N-nitrosamines directly damage colonocyte DNA. 18% CRC risk per 50g."),
            "Heart":(False,"Nitrite oxidises LDL",   "Nitrite radicals oxidise LDL → atherosclerotic plaque initiation."),
            "Lungs":(False,"Sulphite asthma",        "Sulphite preservatives → bronchoconstriction in 5-10% asthmatics."),
            "Liver":(False,"CYP2E1 overload",        "Nitrosamine degradation via CYP2E1 generates reactive oxygen species."),
        },
        "nutrients_added": {"sodium":60,"sat_fat":20,"protein":12},
        "harmful_compounds": {"nitrosamines":1,"sodium_load":1,"sat_fat_lipid":1},
        "gi_index": 48, "macros": {"carbs":4,"protein":12,"fat":18,"fiber":0},
        "microbiome": {"Bacteroidetes":+8,"Bifidobacterium":-10,"Lactobacillus":-8,"Faecalibacterium":-10},
        "orac": 30,
        "hormone_effect": {"insulin":+15,"cortisol":+8,"leptin":0,"ghrelin":+5},
        "circadian": {"morning":0.7,"afternoon":0.6,"evening":0.5},
        "sleep_effect": -3,
    },
    {
        "name": "White Bread", "kind": "mod", "icon": "\U0001f35e",
        "badges": ["sugar","sodium"],
        "profile": "GI ~75. Milling removes 70% zinc, 80% B vitamins, all fiber. Nutritionally indistinguishable from pure glucose. Depletes microbiome within days.",
        "system": {"Energy":+2,"Gut Health":-5,"Inflammation":+5,"Brain Clarity":-3,"Heart Strength":-3},
        "organs": {
            "Brain":(False,"Glucose crash",       "GI 75 → rapid spike → hypoglycaemic rebound → brain fog 1-2h."),
            "Gut":  (False,"Microbiome starvation","Zero prebiotic fiber starves commensals within 48-72h of consistent use."),
            "Heart":(False,"Insulin resistance",  "Chronic spikes → hyperinsulinemia → LDL particle overproduction."),
        },
        "nutrients_added": {"carbs":50,"sodium":18,"protein":6},
        "harmful_compounds": {"agEs":1,"fructose_met":1},
        "gi_index": 75, "macros": {"carbs":50,"protein":9,"fat":2,"fiber":1},
        "microbiome": {"Bifidobacterium":-10,"Lactobacillus":-8,"Faecalibacterium":-7},
        "orac": 60,
        "hormone_effect": {"insulin":+50,"cortisol":+8,"leptin":-7,"ghrelin":+18},
        "circadian": {"morning":0.8,"afternoon":0.7,"evening":0.5},
        "sleep_effect": -3,
    },
    {
        "name": "Ice Cream", "kind": "mod", "icon": "\U0001f366",
        "badges": ["sugar","sat_fat","fructose"],
        "profile": "Fat+sugar 50:50 ratio not found in nature → overrides satiety (Gearhardt hyperpalatable food criteria). Emulsifiers polysorbate-80 + carrageenan erode mucus layer.",
        "system": {"Energy":+2,"Gut Health":-5,"Inflammation":+5,"Brain Clarity":-2},
        "organs": {
            "Gut":  (False,"Emulsifier mucosa damage","P80 + carrageenan = thin mucus layer → bacteria closer to epithelium."),
            "Liver":(False,"Kupffer cell activation","Saturated fat activates hepatic macrophages → inflammatory cascade."),
            "Brain":(False,"Hippocampal suppression","Fat+sugar combo suppresses neurogenesis more than either alone."),
            "Skin": (False,"AGE collagen stiffening",  "Glucose drives glycation of dermal collagen → premature wrinkling."),
        },
        "nutrients_added": {"sugar":28,"sat_fat":14,"carbs":30},
        "harmful_compounds": {"fructose_met":1,"sat_fat_lipid":1,"agEs":1},
        "gi_index": 62, "macros": {"carbs":30,"protein":3,"fat":18,"fiber":0},
        "microbiome": {"Bifidobacterium":-9,"Lactobacillus":-7,"Akkermansia":-6},
        "orac": 40,
        "hormone_effect": {"insulin":+45,"cortisol":+8,"leptin":-8,"ghrelin":+22},
        "circadian": {"morning":0.5,"afternoon":0.7,"evening":0.4},
        "sleep_effect": -4,
    },
]

# ═══════════════════════════════════════════════════════════════
#  BODY SYSTEMS
# ═══════════════════════════════════════════════════════════════
class BodySystems:
    def __init__(self):
        self.reset()

    def reset(self):
        self.values = {
            "Energy":65.0,"Gut Health":65.0,"Inflammation":35.0,
            "Brain Clarity":65.0,"Heart Strength":65.0
        }

    def apply(self, food):
        for k, v in food.get("system",{}).items():
            if k in self.values:
                self.values[k] = max(0.0, min(100.0, self.values[k]+v))

    def score(self):
        v = self.values
        pos = (v["Energy"]+v["Gut Health"]+v["Brain Clarity"]+v["Heart Strength"])/4
        return max(0.0, min(100.0, pos - v["Inflammation"]*0.4))

# ═══════════════════════════════════════════════════════════════
#  NEUROTRANSMITTER STATE
# ═══════════════════════════════════════════════════════════════
class Neurotransmitters:
    def __init__(self):
        self.reset()

    def reset(self):
        self.dopamine   = 65.0
        self.serotonin  = 65.0
        self.cortisol   = 35.0
        self.gaba       = 65.0
        self.norepineph = 55.0

    def apply(self, food):
        kind = food["kind"]
        if kind == "trad":
            self.serotonin  = min(100, self.serotonin  + 4)
            self.gaba       = min(100, self.gaba        + 3)
            self.cortisol   = max(0,   self.cortisol    - 3)
        else:
            self.dopamine   = min(100, self.dopamine    + 8)  # spike then crash
            self.cortisol   = min(100, self.cortisol    + 6)
            self.gaba       = max(0,   self.gaba        - 4)
        # Apply hormone effects
        he = food.get("hormone_effect", {})
        self.cortisol = max(0, min(100, self.cortisol + he.get("cortisol", 0) * 0.5))

# ═══════════════════════════════════════════════════════════════
#  MICROBIOME STATE
# ═══════════════════════════════════════════════════════════════
class Microbiome:
    SPECIES = [
        "Bifidobacterium","Lactobacillus","Faecalibacterium",
        "Akkermansia","Roseburia","Bacteroidetes",
        "Candida","Streptococcus_therm","Leuconostoc","Saccharomyces"
    ]
    GOOD_SPECIES = {"Bifidobacterium","Lactobacillus","Faecalibacterium",
                    "Akkermansia","Roseburia","Streptococcus_therm",
                    "Leuconostoc","Saccharomyces"}
    def __init__(self):
        self.reset()

    def reset(self):
        self.counts = {s: 50.0 for s in self.SPECIES}
        self.counts["Bacteroidetes"] = 35.0
        self.counts["Candida"] = 10.0

    def apply(self, food):
        mb = food.get("microbiome", {})
        for sp, delta in mb.items():
            if sp in self.counts:
                self.counts[sp] = max(0.0, min(100.0, self.counts[sp]+delta))

    def diversity_score(self):
        vals = list(self.counts.values())
        total = sum(vals) or 1
        proportions = [v/total for v in vals if v > 0]
        # Shannon diversity index
        H = -sum(p*math.log(p) for p in proportions if p > 0)
        return min(100.0, H * 30)

# ═══════════════════════════════════════════════════════════════
#  NUTRIENT TRACKER
# ═══════════════════════════════════════════════════════════════
class NutrientTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.levels = {k[0]: 0.0 for k in RDA_NUTRIENTS}

    def apply(self, food):
        added = food.get("nutrients_added", {})
        for k, v in added.items():
            if k in self.levels:
                self.levels[k] = min(200.0, self.levels[k] + v)

    def deficiencies(self):
        return [k for k, v in self.levels.items() if v < 30]

# ═══════════════════════════════════════════════════════════════
#  HORMONE TRACKER
# ═══════════════════════════════════════════════════════════════
class HormoneTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.insulin  = 40.0
        self.cortisol = 35.0
        self.leptin   = 55.0
        self.ghrelin  = 45.0

    def apply(self, food):
        he = food.get("hormone_effect", {})
        self.insulin  = max(0, min(100, self.insulin  + he.get("insulin",0)  * 0.15))
        self.cortisol = max(0, min(100, self.cortisol + he.get("cortisol",0) * 0.2))
        self.leptin   = max(0, min(100, self.leptin   + he.get("leptin",0)   * 0.3))
        self.ghrelin  = max(0, min(100, self.ghrelin  + he.get("ghrelin",0)  * 0.25))

# ═══════════════════════════════════════════════════════════════
#  LIVER DETOX QUEUE
# ═══════════════════════════════════════════════════════════════
class LiverDetoxQueue:
    def __init__(self):
        self.queue = []  # list of {compound, name, hours_remaining, hours_total, col}

    def add(self, compound_key):
        if compound_key not in HARMFUL_COMPOUNDS:
            return
        cdata = HARMFUL_COMPOUNDS[compound_key]
        # Avoid duplicate entries — just refresh timer
        for item in self.queue:
            if item["compound"] == compound_key:
                item["hours_remaining"] = cdata[1]
                return
        self.queue.append({
            "compound": compound_key,
            "name": cdata[0],
            "hours_remaining": float(cdata[1]),
            "hours_total": float(cdata[1]),
            "col": cdata[2],
        })

    def tick(self, dt_hours=0.5):
        """Simulate time passing (called on each drop for simplicity)."""
        for item in self.queue:
            item["hours_remaining"] = max(0, item["hours_remaining"] - dt_hours)
        self.queue = [i for i in self.queue if i["hours_remaining"] > 0]

    def reset(self):
        self.queue.clear()

# ═══════════════════════════════════════════════════════════════
#  BLOOD GLUCOSE SIMULATION
# ═══════════════════════════════════════════════════════════════
class BloodGlucose:
    def __init__(self):
        self.reset()
        self.curve_history = []  # last 80 values

    def reset(self):
        self.baseline  = 85.0
        self.current   = 85.0
        self.peak      = 85.0
        self.t_since   = 0.0
        self.active    = False
        self.gi        = 0
        self.curve_history = [85.0] * 80

    def feed(self, food):
        gi  = food.get("gi_index", 50)
        carbs = food.get("macros", {}).get("carbs", 20)
        self.gi      = gi
        self.peak    = min(250, self.baseline + gi * carbs * 0.018)
        self.current = self.peak
        self.t_since = 0.0
        self.active  = True

    def update(self):
        if self.active:
            self.t_since += 1
            decay = math.exp(-self.t_since / 60)
            self.current = self.baseline + (self.peak - self.baseline) * decay
            if abs(self.current - self.baseline) < 0.5:
                self.active = False
                self.current = self.baseline
        self.curve_history.append(self.current)
        if len(self.curve_history) > 80:
            self.curve_history.pop(0)

# ═══════════════════════════════════════════════════════════════
#  MACRO ACCUMULATOR
# ═══════════════════════════════════════════════════════════════
class MacroAccumulator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.carbs = 0.0; self.protein = 0.0
        self.fat   = 0.0; self.fiber   = 0.0
        self.orac  = 0.0; self.gl      = 0.0  # glycemic load
        self.omega3_ratio = 50.0  # 50 = balanced

    def apply(self, food):
        m = food.get("macros", {})
        self.carbs   += m.get("carbs",   0)
        self.protein += m.get("protein", 0)
        self.fat     += m.get("fat",     0)
        self.fiber   += m.get("fiber",   0)
        self.orac    += food.get("orac", 0)
        gi = food.get("gi_index", 50)
        self.gl      += (gi * m.get("carbs", 0)) / 100
        # Omega balance
        na = food.get("nutrients_added", {})
        o3 = na.get("omega3", 0)
        o6 = na.get("omega6", 0)
        if o3 > 0: self.omega3_ratio = min(100, self.omega3_ratio + 5)
        if o6 > 0: self.omega3_ratio = max(0,   self.omega3_ratio - 3)

# ═══════════════════════════════════════════════════════════════
#  SLEEP SCORE
# ═══════════════════════════════════════════════════════════════
class SleepScore:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 75.0
        self.tonight_delta = 0.0

    def apply(self, food):
        se = food.get("sleep_effect", 0)
        self.tonight_delta += se
        self.score = max(0, min(100, self.score + se * 0.5))

# ═══════════════════════════════════════════════════════════════
#  SUPPLEMENT ENGINE
# ═══════════════════════════════════════════════════════════════
SUPPLEMENT_MAP = {
    "omega3":  ("Fish oil / Algae DHA", "500-2000mg EPA+DHA daily"),
    "vitD":    ("Vitamin D3 + K2",      "2000-4000 IU D3 with 100mcg K2"),
    "magnes":  ("Magnesium glycinate",  "300-400mg before bed"),
    "vitB12":  ("Methylcobalamin B12",  "500-1000mcg sublingual daily"),
    "fiber":   ("Psyllium husk",        "5-10g with water before meals"),
    "probiotic_cfu": ("Multi-strain probiotic", "20-50 billion CFU daily"),
    "vitC":    ("Ascorbic acid",        "500-1000mg daily with food"),
    "zinc":    ("Zinc picolinate",      "15-30mg with food"),
    "folate":  ("Methylfolate (5-MTHF)","400-800mcg daily"),
    "calcium": ("Calcium citrate",      "500mg with meals (2 doses)"),
}

# ═══════════════════════════════════════════════════════════════
#  ORGAN STATE
# ═══════════════════════════════════════════════════════════════
organ_state = {
    name: {"score": 65.0, "glow_col": NEUTRAL, "glow_alpha": 0.0, "speech": "", "speech_timer": 0}
    for name in ORGANS
}

ORGAN_SPEECHES = {
    "Brain":  ["I'm exhausted from sugar spikes!", "Feed me DHA please!", "Cortisol is shrinking me!", "This feels amazing!"],
    "Heart":  ["Trans fats are coating my arteries!", "Omega-3 is protecting me!", "My rhythm is irregular!", "Blood pressure dropping nicely!"],
    "Liver":  ["I'm overloaded with fructose!", "Sulforaphane is helping me detox!", "Acrylamide is damaging my DNA!", "Bile flow is optimal!"],
    "Gut":    ["My microbiome is thriving!", "Emulsifiers are destroying my mucus!", "This fiber is amazing!", "Pathogen bloom detected!"],
    "Lungs":  ["Inflammation cleared!", "This omega-3 is helping my airways!", "Sulphites triggering constriction!", "Curcumin reducing cytokines!"],
    "Skin":   ["AGEs are stiffening my collagen!", "Antioxidants protecting my cells!", "Omega-6 overload - inflamed!", "Vitamin C boosting collagen!"],
}

def pulse_organ(name, good):
    st = organ_state[name]
    st["score"]      = max(0.0, min(100.0, st["score"] + (8.0 if good else -8.0)))
    st["glow_col"]   = GOOD if good else BAD
    st["glow_alpha"] = 240.0
    # Trigger speech bubble
    speeches = ORGAN_SPEECHES.get(name, [])
    if speeches:
        if good:
            st["speech"] = [s for s in speeches if "!" not in s or any(w in s for w in ["amazing","thriving","protecting","helping","optimal","nice"])]
            if not st["speech"]: st["speech"] = speeches[-1]
            else: st["speech"] = st["speech"][0]
        else:
            st["speech"] = [s for s in speeches if any(w in s for w in ["overloaded","destroying","damage","irregular","shrinking","constriction","stiffening","overload"])]
            if not st["speech"]: st["speech"] = speeches[0]
            else: st["speech"] = st["speech"][0]
        st["speech_timer"] = 180

# ═══════════════════════════════════════════════════════════════
#  GLOBAL STATE OBJECTS
# ═══════════════════════════════════════════════════════════════
body        = BodySystems()
neuro       = Neurotransmitters()
microbiome  = Microbiome()
nutrients   = NutrientTracker()
hormones    = HormoneTracker()
liver_queue = LiverDetoxQueue()
glucose     = BloodGlucose()
macros      = MacroAccumulator()
sleep_score = SleepScore()

effect_log    = []
log_scroll    = 0
LOG_ENTRY_H   = 54

hover_food_idx  = None
drag_idx        = None
drag_x          = 0
drag_y          = 0
show_help       = False
time_of_day     = "afternoon"   # morning / afternoon / evening
active_tab      = 0             # 0-5 tabs in right panel

# 7-day history
daily_history = [random.uniform(55, 75) for _ in range(7)]
daily_history[-1] = body.score()

# ═══════════════════════════════════════════════════════════════
#  DIGESTION ANIMATION
# ═══════════════════════════════════════════════════════════════
class DigestionParticle:
    """A bolus of food travelling through the GI tract."""
    def __init__(self, icon, col):
        self.icon  = icon
        self.col   = col
        self.wpts  = gi_waypoints()
        self.idx   = 0
        self.t     = 0.0
        self.x, self.y = self.wpts[0]
        self.state = "travel"
        self.stage_label = GI_STAGE_LABELS[0]
        self.absorption_text = ""
        self.done  = False

    def update(self):
        if self.done or self.idx >= len(self.wpts)-1:
            self.done = True; return
        self.t += 0.018
        if self.t >= 1.0:
            self.t = 0.0
            self.idx += 1
            if self.idx < len(GI_STAGE_LABELS):
                self.stage_label = GI_STAGE_LABELS[self.idx]
            if self.idx in GI_STAGE_ABSORPTION:
                self.absorption_text = GI_STAGE_ABSORPTION[self.idx]
            if self.idx >= len(self.wpts)-1:
                self.done = True; return
        p1 = self.wpts[self.idx]
        p2 = self.wpts[self.idx+1]
        self.x = p1[0] + (p2[0]-p1[0]) * self.t
        self.y = p1[1] + (p2[1]-p1[1]) * self.t

    def draw(self, surf):
        if self.done: return
        # Glow
        gs = pygame.Surface((30,30), pygame.SRCALPHA)
        pygame.draw.circle(gs, self.col[:3], (15,15), 15)
        gs.set_alpha(60)
        surf.blit(gs, (int(self.x)-15, int(self.y)-15))
        ico = FICON_SM.render(self.icon, True, WHITE)
        surf.blit(ico, (int(self.x)-8, int(self.y)-8))

class BezierParticle:
    """Arc travel particle from food card to organ."""
    def __init__(self, icon, sx, sy, tx, ty, col):
        self.icon = icon; self.col = col
        self.sx, self.sy = float(sx), float(sy)
        self.tx, self.ty = float(tx), float(ty)
        self.bx = (sx+tx)/2.0 - 60.0
        self.by = min(sy,ty) - 90.0
        self.cx, self.cy = float(sx), float(sy)
        self.t = 0.0; self.state = "travel"
        self.burst_pts = []

    def update(self):
        if self.state == "travel":
            self.t = min(1.0, self.t+0.022)
            u = self.t
            self.cx = (1-u)**2*self.sx + 2*(1-u)*u*self.bx + u**2*self.tx
            self.cy = (1-u)**2*self.sy + 2*(1-u)*u*self.by + u**2*self.ty
            if self.t >= 1.0:
                self.state = "burst"
                for _ in range(28):
                    ang = random.uniform(0, 2*math.pi)
                    sp  = random.uniform(2.0, 5.5)
                    self.burst_pts.append([self.tx,self.ty,
                        math.cos(ang)*sp, math.sin(ang)*sp,
                        random.randint(35, 65)])
        elif self.state == "burst":
            next_pts = []
            for pt in self.burst_pts:
                pt[0]+=pt[2]; pt[1]+=pt[3]; pt[3]+=0.1; pt[4]-=1
                if pt[4]>0: next_pts.append(pt)
            self.burst_pts = next_pts
            if not self.burst_pts: self.state = "done"

    def draw(self, surf):
        if self.state == "travel":
            ico = FICON_LG.render(self.icon, True, WHITE)
            surf.blit(ico, (int(self.cx)-13, int(self.cy)-13))
        elif self.state == "burst":
            for pt in self.burst_pts:
                alpha = int(255*pt[4]/60)
                rad   = max(2, pt[4]//8)
                s = pygame.Surface((rad*2,rad*2), pygame.SRCALPHA)
                pygame.draw.circle(s, self.col[:3], (rad,rad), rad)
                s.set_alpha(alpha)
                surf.blit(s, (int(pt[0])-rad, int(pt[1])-rad))

class FloatText:
    def __init__(self, x, y, text, col):
        self.x, self.y = float(x), float(y)
        self.text = text; self.col = col
        self.life = 140; self.max_life = 140

    def update(self): self.y -= 0.6; self.life -= 1

    def draw(self, surf):
        alpha   = int(255*self.life/self.max_life)
        rendered = FT.render(self.text, True, self.col)
        tmp = pygame.Surface(rendered.get_size(), pygame.SRCALPHA)
        tmp.blit(rendered,(0,0)); tmp.set_alpha(alpha)
        surf.blit(tmp,(int(self.x)-rendered.get_width()//2, int(self.y)))

fx_bezier   = []
fx_floats   = []
fx_digestion = []

# ═══════════════════════════════════════════════════════════════
#  APPLY FOOD
# ═══════════════════════════════════════════════════════════════
def apply_food(food, organ_name):
    global daily_history
    body.apply(food); neuro.apply(food); microbiome.apply(food)
    nutrients.apply(food); hormones.apply(food)
    glucose.feed(food); macros.apply(food); sleep_score.apply(food)

    # Liver detox queue
    for compound_key in food.get("harmful_compounds", {}):
        liver_queue.add(compound_key)
    liver_queue.tick(dt_hours=1.0)

    # Organ effect
    organs_map = food.get("organs", {})
    if organ_name in organs_map:
        good, lbl, detail = organs_map[organ_name]
    else:
        good   = food["kind"] == "trad"
        lbl    = "+Nourish" if good else "Stress"
        detail = "General nutritional impact."
    pulse_organ(organ_name, good)
    col = GOOD if good else BAD
    ocx, ocy = organ_world(organ_name)
    fx_floats.append(FloatText(ocx, ocy-40, lbl, col))

    # Circadian modifier
    circ = food.get("circadian", {}).get(time_of_day, 1.0)
    if circ < 0.8:
        fx_floats.append(FloatText(ocx, ocy-60, f"Poor timing ({time_of_day})", WARN))

    effect_log.insert(0, {
        "food":food["name"],"organ":organ_name,
        "good":good,"lbl":lbl,"detail":detail,"icon":food["icon"],
    })
    # Update history
    daily_history[-1] = body.score()

    # Launch digestion animation
    fx_digestion.append(DigestionParticle(food["icon"],
                         TRAD if food["kind"]=="trad" else MOD))

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def organ_world(name):
    o = ORGANS[name]; dx, dy = o["rel"]
    return BODY_CX + sx(dx), BODY_TOP + sy(dy)

def organ_at(px, py):
    for name, o in ORGANS.items():
        cx, cy = organ_world(name)
        ex = float((sx(o["hit_rx"]) + sx(14)) ** 2)
        ey = float((sy(o["hit_ry"]) + sy(14)) ** 2)
        if (px-cx)**2/ex + (py-cy)**2/ey <= 1.0:
            return name
    return None

def on_body(px, py):
    return (LEFT_W + sx(10) < px < W - RIGHT_W - sx(10) and
            BODY_TOP - sy(10) < py < BODY_TOP + sy(430))

CARD_COLS  = 2
CARD_PAD_X = sx(7)
CARD_PAD_Y = sy(5)

def card_rect(i):
    col = i % CARD_COLS; row = i // CARD_COLS
    x   = CARD_PAD_X + col * (CARD_W + CARD_PAD_X)
    y   = sy(118) + row * (CARD_H + CARD_PAD_Y)
    return pygame.Rect(x, y, CARD_W, CARD_H)

def reset_all():
    body.reset(); neuro.reset(); microbiome.reset()
    nutrients.reset(); hormones.reset(); liver_queue.reset()
    glucose.reset(); macros.reset(); sleep_score.reset()
    for st in organ_state.values():
        st["score"]=65.0; st["glow_alpha"]=0.0; st["speech"]=""; st["speech_timer"]=0
    effect_log.clear(); fx_bezier.clear(); fx_floats.clear(); fx_digestion.clear()
    global daily_history, log_scroll
    daily_history = [random.uniform(55, 75) for _ in range(7)]
    daily_history[-1] = body.score()
    log_scroll = 0

# ═══════════════════════════════════════════════════════════════
#  DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════
def draw_bar(surf, x, y, w, h, value, max_val, col, bg=(28,32,55), label=None, val_str=None):
    pygame.draw.rect(surf, bg, (x,y,w,h), border_radius=h//2)
    fill = max(0, int(w * min(value,max_val) / max_val))
    if fill > 0:
        pygame.draw.rect(surf, col, (x,y,fill,h), border_radius=h//2)
    if label:
        surf.blit(FSS.render(label, True, LGREY), (x, y-14))
    if val_str:
        vs = FSS.render(val_str, True, WHITE)
        surf.blit(vs, (x+w-vs.get_width(), y-14))

def draw_meter(surf, x, y, w, h, value, col, inverted=False):
    """Draw a horizontal meter. inverted=True means lower is better."""
    pygame.draw.rect(surf, (28,32,55), (x,y,w,h), border_radius=h//2)
    visual = (100-value) if inverted else value
    fill = int(w * visual / 100)
    if fill > 0:
        pygame.draw.rect(surf, col, (x,y,fill,h), border_radius=h//2)
    # Midpoint marker
    mid = x + w//2
    pygame.draw.line(surf, DIVIDER, (mid, y-2), (mid, y+h+2), 1)

# ═══════════════════════════════════════════════════════════════
#  DRAW: GI TRACT PATHWAY
# ═══════════════════════════════════════════════════════════════
def draw_gi_tract():
    pts = gi_waypoints()
    if len(pts) >= 2:
        for i in range(len(pts)-1):
            p1, p2 = pts[i], pts[i+1]
            seg_col = (50, 70, 50) if i < 5 else (40, 65, 40)
            pygame.draw.line(screen, seg_col, p1, p2, 3)
    for pt in pts:
        pygame.draw.circle(screen, (45, 65, 45), pt, 3)

# ═══════════════════════════════════════════════════════════════
#  DRAW: BODY SILHOUETTE
# ═══════════════════════════════════════════════════════════════
def draw_body_silhouette():
    cx = BODY_CX; top = BODY_TOP

    def fr(rect, r=12):
        pygame.draw.rect(screen, BODY_FILL, rect, border_radius=r)
        pygame.draw.rect(screen, BODY_EDGE, rect, 2, border_radius=r)

    def fe(rect):
        pygame.draw.ellipse(screen, BODY_FILL, rect)
        pygame.draw.ellipse(screen, BODY_EDGE, rect, 2)

    fe(pygame.Rect(cx-40, top, 80, 82))               # head
    fr(pygame.Rect(cx-16, top+74,  32, 28), 6)        # neck
    fr(pygame.Rect(cx-74, top+98, 148,248), 16)       # torso
    fr(pygame.Rect(cx-116,top+104, 44,172), 18)       # L arm
    fr(pygame.Rect(cx-122,top+268, 40, 72), 14)
    fr(pygame.Rect(cx+72, top+104, 44,172), 18)       # R arm
    fr(pygame.Rect(cx+82, top+268, 40, 72), 14)
    fr(pygame.Rect(cx-68, top+338,136, 62), 20)       # pelvis
    fr(pygame.Rect(cx-66, top+385, 56,185), 16)       # L leg
    fr(pygame.Rect(cx-68, top+558, 58, 56), 10)
    fr(pygame.Rect(cx+10, top+385, 56,185), 16)       # R leg
    fr(pygame.Rect(cx+10, top+558, 58, 56), 10)
    pygame.draw.line(screen, BODY_EDGE,(cx-32,top+100),(cx,top+112),2)
    pygame.draw.line(screen, BODY_EDGE,(cx+32,top+100),(cx,top+112),2)

# ═══════════════════════════════════════════════════════════════
#  DRAW: INFLAMMATION HEATMAP
# ═══════════════════════════════════════════════════════════════
def draw_inflammation_heatmap():
    inflam = body.values["Inflammation"]
    if inflam < 20: return
    alpha = int(min(inflam * 1.2, 60))
    hs = pygame.Surface((sx(160), sy(350)), pygame.SRCALPHA)
    hs.fill((200, 50, 50))
    hs.set_alpha(alpha)
    screen.blit(hs, (BODY_CX - sx(80), BODY_TOP + sy(95)))

# ═══════════════════════════════════════════════════════════════
#  DRAW: ORGANS
# ═══════════════════════════════════════════════════════════════
def draw_organs():
    now = time.time()
    for name, o in ORGANS.items():
        cx, cy  = organ_world(name)
        st      = organ_state[name]

        pulse = 1.0 + 0.05 * math.sin(now*2.5 + hash(name)*1.3)
        prx = int(o["hit_rx"] * pulse * 0.85)
        pry = int(o["hit_ry"] * pulse * 0.85)

        # Glow halo
        if st["glow_alpha"] > 0.0:
            gsurf = pygame.Surface((prx*2+40, pry*2+40), pygame.SRCALPHA)
            ga = int(min(st["glow_alpha"], 100))
            pygame.draw.ellipse(gsurf, st["glow_col"][:3], (0,0,prx*2+40,pry*2+40))
            gsurf.set_alpha(ga)
            screen.blit(gsurf,(cx-prx-20, cy-pry-20))
            st["glow_alpha"] = max(0.0, st["glow_alpha"]-1.6)

        # Health-tinted colour
        sc = st["score"]
        if sc > 60:
            tf  = min(1.0,(sc-60)/40); base = o["col"]
            col = tuple(int(base[i]+(GOOD[i]-base[i])*tf*0.35) for i in range(3))
        else:
            tf  = min(1.0,(60-sc)/60); base = o["col"]
            col = tuple(int(base[i]+(BAD[i]-base[i])*tf*0.4) for i in range(3))

        edge_c = st["glow_col"] if st["glow_alpha"]>20 else tuple(min(255,int(c*1.4)) for c in o["col"])

        # Draw anatomical shape
        draw_organ_shape(screen, name, cx, cy, col, edge_c)

        # Label
        lbl = FORD.render(name, True, WHITE)
        screen.blit(lbl,(cx-lbl.get_width()//2, cy-lbl.get_height()//2))

        # Mini health bar
        bw = prx*2 - 2
        pygame.draw.rect(screen,(28,32,55),(cx-bw//2, cy+pry+5, bw, 4),border_radius=2)
        fw = int(bw*sc/100)
        bc = GOOD if sc>60 else (BAD if sc<40 else NEUTRAL)
        if fw>0: pygame.draw.rect(screen,bc,(cx-bw//2,cy+pry+5,fw,4),border_radius=2)

        # Speech bubble
        if st["speech_timer"] > 0 and st["speech"]:
            st["speech_timer"] -= 1
            alpha = min(255, st["speech_timer"]*3)
            btext = FSS.render(st["speech"], True, WHITE)
            bw2   = btext.get_width() + 12
            bh2   = 18
            bx    = cx + prx + 6
            by    = cy - 10
            bsurf = pygame.Surface((bw2, bh2), pygame.SRCALPHA)
            pygame.draw.rect(bsurf,(20,22,45),(0,0,bw2,bh2),border_radius=5)
            pygame.draw.rect(bsurf,(100,120,180),(0,0,bw2,bh2),2,border_radius=5)
            bsurf.set_alpha(alpha)
            screen.blit(bsurf,(bx,by))
            ts = pygame.Surface(btext.get_size(), pygame.SRCALPHA)
            ts.blit(btext,(0,0)); ts.set_alpha(alpha)
            screen.blit(ts,(bx+6, by+1))

# ═══════════════════════════════════════════════════════════════
#  DRAW: DROP HINTS
# ═══════════════════════════════════════════════════════════════
def draw_drop_hints():
    if drag_idx is None: return
    now = time.time()
    for name, o in ORGANS.items():
        cx, cy = organ_world(name)
        hrx = sx(o["hit_rx"]) + sx(8)
        hry = sy(o["hit_ry"]) + sy(8)
        hs = pygame.Surface((hrx*2, hry*2), pygame.SRCALPHA)
        a  = int(30 + 22*math.sin(now*4))
        pygame.draw.ellipse(hs,(255,255,255),(0,0,hrx*2,hry*2))
        hs.set_alpha(a)
        screen.blit(hs,(cx-hrx, cy-hry))
        hs2 = pygame.Surface((hrx*2, hry*2), pygame.SRCALPHA)
        pygame.draw.ellipse(hs2,(255,255,255),(0,0,hrx*2,hry*2),2)
        hs2.set_alpha(110)
        screen.blit(hs2,(cx-hrx, cy-hry))

# ═══════════════════════════════════════════════════════════════
#  DRAW: FOOD PANEL
# ═══════════════════════════════════════════════════════════════
def draw_food_panel():
    pygame.draw.rect(screen, PANEL_L, (0,0,LEFT_W,H))
    pygame.draw.line(screen, DIVIDER,(LEFT_W,0),(LEFT_W,H),2)

    screen.blit(FH.render("Foods",True,WHITE),(sx(10),sy(12)))
    screen.blit(FS.render("Drag onto body",True,GREY),(sx(10),sy(42)))
    screen.blit(FS.render("Traditional",True,TRAD),(sx(10),sy(60)))
    screen.blit(FS.render("Modern",True,MOD),(sx(110),sy(60)))
    pygame.draw.line(screen,DIVIDER,(sx(6),sy(80)),(LEFT_W-sx(6),sy(80)),1)

    for i, food in enumerate(FOODS):
        if i == drag_idx: continue
        rect = card_rect(i)
        if rect.y > H - sy(60): continue
        col = TRAD if food["kind"]=="trad" else MOD
        bg  = (col[0]//6, col[1]//6, col[2]//6)
        if i == hover_food_idx:
            bg = (col[0]//3, col[1]//3, col[2]//3)
        pygame.draw.rect(screen, bg,  rect, border_radius=ss(9))
        pygame.draw.rect(screen, col, rect, (2 if i==hover_food_idx else 1), border_radius=ss(9))

        screen.blit(FICON_MD.render(food["icon"],True,WHITE),(rect.x+sx(4),rect.y+sy(4)))
        lines = textwrap.wrap(food["name"],10)
        for li,line in enumerate(lines[:2]):
            screen.blit(FSS.render(line,True,WHITE),(rect.x+sx(4),rect.y+sy(34)+li*sy(12)))

        bx = rect.x+sx(3); by = rect.y+rect.h-sy(14)
        for bk in food["badges"][:2]:
            bd = BADGE_DEFS.get(bk)
            if not bd: continue
            blbl = FSS.render(bd[0],True,WHITE); bw = blbl.get_width()+sx(4)
            if bx+bw > rect.right-1: break
            pygame.draw.rect(screen,bd[1],(bx,by,bw,sy(12)),border_radius=3)
            screen.blit(blbl,(bx+sx(2),by+1)); bx += bw+sx(2)

    screen.blit(FSS.render("Hover=nutrition  H=help  R=reset",True,GREY),(sx(4),H-sy(44)))
    time_col = (100,160,255) if time_of_day=="morning" else ((255,200,50) if time_of_day=="afternoon" else (100,80,180))
    screen.blit(FSS.render(f"T=time: {time_of_day}",True,time_col),(sx(4),H-sy(26)))

# ═══════════════════════════════════════════════════════════════
#  DRAW: HOVER PROFILE
# ═══════════════════════════════════════════════════════════════
def draw_hover_profile():
    if hover_food_idx is None or drag_idx is not None: return
    food    = FOODS[hover_food_idx]
    col     = TRAD if food["kind"]=="trad" else MOD
    wrapped = textwrap.wrap(food["profile"], 42)
    tw = sx(325); th = sy(58) + len(wrapped)*sy(15) + sy(36)
    tx = LEFT_W + sx(14)
    ty = max(sy(8), min(card_rect(hover_food_idx).y - sy(8), H-th-sy(8)))

    panel = pygame.Surface((tw,th), pygame.SRCALPHA)
    pygame.draw.rect(panel,(18,20,42),(0,0,tw,th),border_radius=ss(12))
    panel.set_alpha(235)
    screen.blit(panel,(tx,ty))
    pborder = pygame.Surface((tw,th), pygame.SRCALPHA)
    pygame.draw.rect(pborder, col,(0,0,tw,th),2,border_radius=ss(12))
    pborder.set_alpha(180)
    screen.blit(pborder,(tx,ty))
    screen.blit(FICON_LG.render(food["icon"],True,WHITE),(tx+sx(7),ty+sy(7)))
    screen.blit(FT.render(food["name"],True,WHITE),(tx+sx(42),ty+sy(8)))
    kl = "Traditional" if food["kind"]=="trad" else "Modern / Processed"
    screen.blit(FS.render(kl,True,col),(tx+sx(42),ty+sy(30)))
    py_ = ty+sy(52)
    for line in wrapped:
        screen.blit(FSS.render(line,True,LGREY),(tx+sx(7),py_)); py_+=sy(15)
    py_+=sy(4)
    bx_ = tx+sx(7)
    for bk in food["badges"]:
        bd = BADGE_DEFS.get(bk)
        if not bd: continue
        blbl = FSS.render(bd[0],True,WHITE); bw_ = blbl.get_width()+sx(7)
        if bx_+bw_ > tx+tw-sx(6): bx_=tx+sx(7); py_+=sy(16)
        pygame.draw.rect(screen,bd[1],(bx_,py_,bw_,sy(14)),border_radius=4)
        screen.blit(blbl,(bx_+sx(4),py_+sy(2))); bx_+=bw_+sx(4)
    py_ += sy(18)
    gi_s = FSS.render(f"GI={food['gi_index']}  |  Carbs={food['macros']['carbs']}g  Protein={food['macros']['protein']}g  Fat={food['macros']['fat']}g", True, GREY)
    screen.blit(gi_s,(tx+sx(7),py_))

# ═══════════════════════════════════════════════════════════════
#  TABS DEFINITION
# ═══════════════════════════════════════════════════════════════
TABS = ["Systems", "Nutrients", "Gut", "Hormones", "Liver", "Stats"]

# ═══════════════════════════════════════════════════════════════
#  DRAW: RIGHT PANEL — TAB BAR
# ═══════════════════════════════════════════════════════════════
def draw_tab_bar():
    rx = W - RIGHT_W
    tab_w = RIGHT_W // len(TABS)
    for i, tab in enumerate(TABS):
        tx_ = rx + i * tab_w
        active = (i == active_tab)
        bg = (30,35,65) if active else PANEL_R
        pygame.draw.rect(screen, bg, (tx_, 0, tab_w, TAB_H))
        border_c = ACCENT if active else DIVIDER
        pygame.draw.rect(screen, border_c, (tx_, 0, tab_w, TAB_H), 1)
        lbl = FTAB.render(tab, True, WHITE if active else GREY)
        screen.blit(lbl,(tx_+tab_w//2-lbl.get_width()//2, TAB_H//2-lbl.get_height()//2))
    pygame.draw.line(screen, DIVIDER, (rx, TAB_H),(W, TAB_H),1)

# ═══════════════════════════════════════════════════════════════
#  DRAW: TAB 0 — SYSTEMS
# ═══════════════════════════════════════════════════════════════
def draw_tab_systems():
    rx = W - RIGHT_W; y = TAB_H + sy(10)
    p = sx(8)   # standard left padding inside panel

    sc = body.score()
    score_col = (
        int(BAD[0]+(GOOD[0]-BAD[0])*sc/100),
        int(BAD[1]+(GOOD[1]-BAD[1])*sc/100),
        int(BAD[2]+(GOOD[2]-BAD[2])*sc/100),
    )
    sc_surf = FNUM.render(f"{sc:.0f}", True, score_col)
    screen.blit(sc_surf,(W-sc_surf.get_width()-p, y))
    screen.blit(FSS.render("health score",True,GREY),(W-sx(82), y+sy(24)))
    pygame.draw.line(screen,DIVIDER,(rx+p, y+sy(40)),(W-p, y+sy(40)),1)
    y += sy(48)

    for sname, sval in body.values.items():
        mc = METER_COLS[sname]
        screen.blit(FB.render(sname,True,WHITE),(rx+p,y))
        vs = FBD.render(f"{sval:.0f}",True,mc)
        screen.blit(vs,(W-vs.get_width()-p,y))
        is_inv = (sname=="Inflammation")
        draw_meter(screen, rx+p, y+sy(18), RIGHT_W-sx(18), sy(9), sval, mc, inverted=is_inv)
        if is_inv:
            screen.blit(FSS.render("lower=better",True,(60,65,100)),(rx+p+sx(2),y+sy(30)))
        y += (sy(46) if is_inv else sy(34))

    pygame.draw.line(screen,DIVIDER,(rx+p,y+sy(2)),(W-p,y+sy(2)),1); y+=sy(8)

    screen.blit(FB.render("Blood glucose",True,WHITE),(rx+p,y))
    gc_col = GOOD if glucose.current < 140 else (WARN if glucose.current < 180 else BAD)
    gv = FBD.render(f"{glucose.current:.0f} mg/dL",True,gc_col)
    screen.blit(gv,(W-gv.get_width()-p,y)); y+=sy(18)
    cw = RIGHT_W-sx(16); ch = sy(36)
    pygame.draw.rect(screen,(20,24,44),(rx+p,y,cw,ch),border_radius=4)
    hist = glucose.curve_history
    if len(hist) > 1:
        step = cw / (len(hist)-1)
        mn, mx2 = 60, max(200, max(hist)+10)
        pts = [(rx+p+int(i*step), y+ch-int((v-mn)/(mx2-mn)*ch)) for i,v in enumerate(hist)]
        pygame.draw.lines(screen, gc_col, False, pts, 1)
    dl = y + ch - int((140-60)/(max(200,max(hist)+10)-60)*ch)
    pygame.draw.line(screen, (255,150,50), (rx+p,dl),(rx+p+cw,dl), 1)
    y += ch + sy(8)

    screen.blit(FB.render("7-day health",True,WHITE),(rx+p,y)); y+=sy(16)
    cw2=RIGHT_W-sx(16); ch2=sy(30)
    pygame.draw.rect(screen,(20,24,44),(rx+p,y,cw2,ch2),border_radius=4)
    if len(daily_history) > 1:
        step2 = cw2/(len(daily_history)-1)
        pts2 = [(rx+p+int(i*step2), y+ch2-int(v/100*ch2)) for i,v in enumerate(daily_history)]
        pygame.draw.lines(screen,ACCENT,False,pts2,2)
    y += ch2+sy(8)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(8)
    screen.blit(FB.render("Sleep quality tonight",True,WHITE),(rx+p,y))
    sc_sleep_col = GOOD if sleep_score.score > 65 else (WARN if sleep_score.score > 40 else BAD)
    ss_surf = FBD.render(f"{sleep_score.score:.0f}%",True,sc_sleep_col)
    screen.blit(ss_surf,(W-ss_surf.get_width()-p,y)); y+=sy(18)
    draw_meter(screen,rx+p,y,RIGHT_W-sx(18),sy(8),sleep_score.score,(100,140,220)); y+=sy(20)
    delta_s = sleep_score.tonight_delta
    ds_col = GOOD if delta_s>=0 else BAD
    screen.blit(FSS.render(f"Diet effect: {'+' if delta_s>=0 else ''}{delta_s:.0f} pts",True,ds_col),(rx+p,y))

# ═══════════════════════════════════════════════════════════════
#  DRAW: TAB 1 — NUTRIENTS
# ═══════════════════════════════════════════════════════════════
def draw_tab_nutrients():
    rx = W - RIGHT_W; y = TAB_H + sy(8); p = sx(8)

    screen.blit(FBD.render("Daily macros",True,WHITE),(rx+p,y)); y+=sy(18)
    total_cal = macros.carbs*4 + macros.protein*4 + macros.fat*9
    screen.blit(FSS.render(f"Total: {total_cal:.0f} kcal  |  GL: {macros.gl:.0f}",True,GREY),(rx+p,y)); y+=sy(14)
    for mname, mval, mcol, rda in [
        ("Carbs",   macros.carbs,   (220,185,60), 130),
        ("Protein", macros.protein, (100,170,220),56),
        ("Fat",     macros.fat,     (215,130,50), 78),
        ("Fiber",   macros.fiber,   (60,185,100), 38),
    ]:
        draw_bar(screen,rx+p,y+sy(14),RIGHT_W-sx(16),sy(7),mval,rda*1.5,mcol,
                 label=mname,val_str=f"{mval:.0f}g"); y+=sy(28)

    screen.blit(FSS.render(f"ORAC antioxidants: {macros.orac:.0f}",True,LGREY),(rx+p,y)); y+=sy(14)
    draw_bar(screen,rx+p,y,RIGHT_W-sx(16),sy(6),macros.orac,5000,(175,80,210)); y+=sy(16)

    screen.blit(FSS.render(f"Omega-3:6 balance: {macros.omega3_ratio:.0f}/100",True,LGREY),(rx+p,y)); y+=sy(14)
    o3c = GOOD if macros.omega3_ratio>50 else (WARN if macros.omega3_ratio>30 else BAD)
    draw_bar(screen,rx+p,y,RIGHT_W-sx(16),sy(6),macros.omega3_ratio,100,o3c); y+=sy(16)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(6)

    screen.blit(FBD.render("Nutrient RDA tracker",True,WHITE),(rx+p,y)); y+=sy(18)
    defics = nutrients.deficiencies()
    if defics:
        screen.blit(FSS.render(f"Low: {', '.join(defics[:4])}",True,WARN),(rx+p,y)); y+=sy(14)

    bar_h = H - y - sy(50)
    screen.set_clip(pygame.Rect(rx, y, RIGHT_W, bar_h))
    for key, disp, rda, ncol in RDA_NUTRIENTS:
        if y > H - sy(55): break
        val = nutrients.levels.get(key, 0)
        col2 = ncol if val >= 30 else (WARN if val >= 15 else BAD)
        draw_bar(screen, rx+p, y+sy(14), RIGHT_W-sx(16), sy(5), val, 100, col2,
                 label=disp, val_str=f"{val:.0f}%")
        y += sy(26)
    screen.set_clip(None)

    defics_all = nutrients.deficiencies()
    if defics_all:
        pygame.draw.line(screen,DIVIDER,(rx+p,H-sy(50)),(W-p,H-sy(50)),1)
        supp = SUPPLEMENT_MAP.get(defics_all[0])
        if supp:
            screen.blit(FSS.render(f"Rx: {supp[0]}",True,GOLD),(rx+p,H-sy(44)))
            screen.blit(FSS.render(supp[1],True,LGREY),(rx+p,H-sy(28)))


def draw_tab_gut():
    rx = W - RIGHT_W; y = TAB_H + sy(8); p = sx(8)

    div = microbiome.diversity_score()
    div_col = GOOD if div>65 else (WARN if div>40 else BAD)
    screen.blit(FBD.render("Microbiome",True,WHITE),(rx+p,y))
    ds = FBD.render(f"Diversity: {div:.0f}",True,div_col)
    screen.blit(ds,(W-ds.get_width()-p,y)); y+=sy(18)
    draw_meter(screen,rx+p,y,RIGHT_W-sx(18),sy(10),div,div_col); y+=sy(20)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(6)

    screen.blit(FS.render("Species abundance",True,LGREY),(rx+p,y)); y+=sy(16)
    for sp, cnt in microbiome.counts.items():
        sp_col = TRAD if sp in microbiome.GOOD_SPECIES else MOD
        screen.blit(FSS.render(sp[:20],True,LGREY),(rx+p,y)); y+=sy(13)
        draw_bar(screen,rx+p,y,RIGHT_W-sx(16),sy(5),cnt,100,sp_col); y+=sy(10)
    y += sy(4)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(6)

    screen.blit(FBD.render("Active digestion",True,WHITE),(rx+p,y)); y+=sy(16)
    active_di = [d for d in fx_digestion if not d.done]
    if active_di:
        d = active_di[0]
        screen.blit(FS.render(f"Stage: {d.stage_label}",True,GOLD),(rx+p,y)); y+=sy(16)
        if d.absorption_text:
            for line in textwrap.wrap(d.absorption_text, 34):
                screen.blit(FSS.render(line,True,LGREY),(rx+p,y)); y+=sy(13)
    else:
        screen.blit(FSS.render("No food in transit",True,GREY),(rx+p,y))


def draw_tab_hormones():
    rx = W - RIGHT_W; y = TAB_H + sy(8); p = sx(8)

    screen.blit(FBD.render("Hormones",True,WHITE),(rx+p,y)); y+=sy(20)

    for hname, hval, hcol, inv, hdesc in [
        ("Insulin",  hormones.insulin,  (255,190,50), False, "Fuel storage signal"),
        ("Cortisol", hormones.cortisol, (220,90,60),  True,  "Stress, lower=better"),
        ("Leptin",   hormones.leptin,   (100,200,130),False, "Satiety signal"),
        ("Ghrelin",  hormones.ghrelin,  (200,140,220),True,  "Hunger, lower=better"),
    ]:
        screen.blit(FB.render(hname,True,WHITE),(rx+p,y))
        hv = FBD.render(f"{hval:.0f}",True,hcol); screen.blit(hv,(W-hv.get_width()-p,y))
        screen.blit(FSS.render(hdesc,True,GREY),(rx+p,y+sy(16)))
        draw_meter(screen,rx+p,y+sy(28),RIGHT_W-sx(18),sy(8),hval,hcol,inverted=inv)
        y += sy(48)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(8)

    screen.blit(FBD.render("Neurotransmitters",True,WHITE),(rx+p,y)); y+=sy(20)
    for nname, nval, ncol in [
        ("Dopamine",    neuro.dopamine,   (180,100,220)),
        ("Serotonin",   neuro.serotonin,  (100,200,150)),
        ("Cortisol",    neuro.cortisol,   (220,90,60)),
        ("GABA",        neuro.gaba,       (100,180,220)),
        ("Norepineph.", neuro.norepineph, (220,160,60)),
    ]:
        screen.blit(FS.render(nname,True,WHITE),(rx+p,y))
        nv = FBD.render(f"{nval:.0f}",True,ncol); screen.blit(nv,(W-nv.get_width()-p,y))
        draw_meter(screen,rx+p,y+sy(15),RIGHT_W-sx(18),sy(6),nval,ncol); y+=sy(30)


def draw_tab_liver():
    rx = W - RIGHT_W; y = TAB_H + sy(8); p = sx(8)

    screen.blit(FBD.render("Liver detox queue",True,WHITE),(rx+p,y)); y+=sy(8)
    screen.blit(FSS.render("Compounds awaiting clearance",True,GREY),(rx+p,y)); y+=sy(20)

    if not liver_queue.queue:
        screen.blit(FS.render("Liver clear — no toxins queued",True,GOOD),(rx+p,y)); y+=sy(24)
    else:
        for item in liver_queue.queue:
            screen.blit(FS.render(item["name"],True,item["col"]),(rx+p,y))
            hr_s = FSS.render(f"{item['hours_remaining']:.0f}h remaining",True,LGREY)
            screen.blit(hr_s,(W-hr_s.get_width()-p,y)); y+=sy(16)
            pct = item["hours_remaining"]/item["hours_total"]
            draw_bar(screen,rx+p,y,RIGHT_W-sx(16),sy(8),pct*100,100,item["col"]); y+=sy(16)
            if item["hours_remaining"] > item["hours_total"]*0.5:
                screen.blit(FSS.render("Hydrate + rest to accelerate clearance",True,GREY),(rx+p,y)); y+=sy(12)
        y += sy(4)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(8)

    total_h = sum(i["hours_remaining"] for i in liver_queue.queue)
    screen.blit(FBD.render("Total liver load",True,WHITE),(rx+p,y)); y+=sy(18)
    load_col = GOOD if total_h==0 else (WARN if total_h<48 else BAD)
    ls = FNUM.render(f"{total_h:.0f}h",True,load_col); screen.blit(ls,(rx+p,y)); y+=sy(30)
    screen.blit(FSS.render("How long until body fully clears",True,GREY),(rx+p,y)); y+=sy(16)
    screen.blit(FSS.render("all consumed harmful compounds.",True,GREY),(rx+p,y)); y+=sy(20)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(8)
    screen.blit(FBD.render("Accelerate detox",True,WHITE),(rx+p,y)); y+=sy(18)
    for tip in ["Drink 8+ glasses of water daily",
                "Exercise increases CYP450 activity",
                "Cruciferous veg upregulate Phase 2",
                "Sleep is the liver's peak detox window"]:
        screen.blit(FSS.render(f"• {tip}",True,LGREY),(rx+p,y)); y+=sy(14)


def draw_tab_stats():
    rx = W - RIGHT_W; y = TAB_H + sy(8); p = sx(8)

    screen.blit(FBD.render("Session statistics",True,WHITE),(rx+p,y)); y+=sy(18)

    total_foods = len(effect_log)
    trad_count  = sum(1 for e in effect_log if any(f["name"]==e["food"] and f["kind"]=="trad" for f in FOODS))
    good_effects= sum(1 for e in effect_log if e["good"])

    for label, val, scol in [
        ("Foods consumed",   str(total_foods),                         WHITE),
        ("Traditional",      str(trad_count),                          TRAD),
        ("Processed",        str(total_foods-trad_count),              MOD),
        ("Positive effects", str(good_effects),                        GOOD),
        ("Neg. effects",     str(total_foods-good_effects),            BAD),
        ("Total calories",   f"{macros.carbs*4+macros.protein*4+macros.fat*9:.0f}", LGREY),
        ("Glycemic load",    f"{macros.gl:.1f}",                       WARN if macros.gl>80 else GOOD),
        ("ORAC score",       f"{macros.orac:.0f}",                     (180,100,220)),
        ("Microbiome div.",  f"{microbiome.diversity_score():.0f}/100",TRAD),
        ("Sleep forecast",   f"{sleep_score.score:.0f}%",              GOOD if sleep_score.score>65 else WARN),
    ]:
        screen.blit(FS.render(label,True,GREY),(rx+p,y))
        vs = FBD.render(val,True,scol); screen.blit(vs,(W-vs.get_width()-p,y)); y+=sy(22)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(8)

    screen.blit(FBD.render("Organ health report",True,WHITE),(rx+p,y)); y+=sy(18)
    for name in ORGANS:
        sc = organ_state[name]["score"]
        grade = "A" if sc>=80 else ("B" if sc>=65 else ("C" if sc>=50 else ("D" if sc>=35 else "F")))
        gc = GOOD if sc>=65 else (WARN if sc>=40 else BAD)
        screen.blit(FS.render(f"{name}:",True,GREY),(rx+p,y))
        gv = FBD.render(grade,True,gc); screen.blit(gv,(W-gv.get_width()-p,y)); y+=sy(20)

    pygame.draw.line(screen,DIVIDER,(rx+p,y),(W-p,y),1); y+=sy(8)

    screen.blit(FBD.render("Recent effects",True,WHITE),(rx+p,y)); y+=sy(18)
    for entry in effect_log[:6]:
        ecol = GOOD if entry["good"] else BAD
        screen.blit(FSS.render(f"{entry['icon']} {entry['food'][:12]} -> {entry['organ']}",True,ecol),(rx+p,y)); y+=sy(14)

# ═══════════════════════════════════════════════════════════════
#  DRAW: RIGHT PANEL DISPATCHER
# ═══════════════════════════════════════════════════════════════
def draw_right_panel():
    rx = W - RIGHT_W
    pygame.draw.rect(screen, PANEL_R, (rx,0,RIGHT_W,H))
    pygame.draw.line(screen, DIVIDER,(rx,0),(rx,H),2)
    draw_tab_bar()

    clip = pygame.Rect(rx, TAB_H+1, RIGHT_W, H-TAB_H-1)
    screen.set_clip(clip)
    if   active_tab == 0: draw_tab_systems()
    elif active_tab == 1: draw_tab_nutrients()
    elif active_tab == 2: draw_tab_gut()
    elif active_tab == 3: draw_tab_hormones()
    elif active_tab == 4: draw_tab_liver()
    elif active_tab == 5: draw_tab_stats()
    screen.set_clip(None)

# ═══════════════════════════════════════════════════════════════
#  DRAW: BOTTOM PANEL — DIGESTION PIPELINE
# ═══════════════════════════════════════════════════════════════
def draw_bottom_panel():
    by = H - BOT_H
    pygame.draw.rect(screen, PANEL_BOT, (LEFT_W, by, W-LEFT_W-RIGHT_W, BOT_H))
    pygame.draw.line(screen, DIVIDER,(LEFT_W,by),(W-RIGHT_W,by),2)

    mid = W - LEFT_W - RIGHT_W
    cx0 = LEFT_W

    screen.blit(FBD.render("Digestion pipeline",True,WHITE),(cx0+sx(10),by+sy(6)))

    stage_positions = [
        ("Mouth",    "\U0001f444", cx0+sx(50)),
        ("Stomach",  "\u2B21",     cx0+sx(160)),
        ("Duodenum", "\u25CB",     cx0+sx(260)),
        ("Jejunum",  "\u25CB",     cx0+sx(350)),
        ("Colon",    "\u25A0",     cx0+sx(440)),
        ("Rectum",   "\u25BC",     cx0+sx(530)),
    ]
    active_di = [d for d in fx_digestion if not d.done]
    current_stage = active_di[0].stage_label if active_di else ""
    last_sx = cx0+sx(530)

    for sname, sicon, stx in stage_positions:
        active = any(sname.lower() in current_stage.lower() for d in active_di)
        col2 = GOLD if active else GREY
        if stx < last_sx:
            pygame.draw.line(screen,(40,50,80),(stx+sx(24),by+sy(38)),(stx+sx(80),by+sy(38)),2)
        lbl = FS.render(sname,True,col2)
        screen.blit(lbl,(stx-lbl.get_width()//2+sx(16), by+sy(50)))

    if active_di:
        d = active_di[0]
        desc = d.absorption_text or f"Transiting: {d.stage_label}"
        for i, line in enumerate(textwrap.wrap(desc, 70)):
            screen.blit(FS.render(line,True,LGREY),(cx0+sx(10), by+sy(72)+i*sy(16)))

    screen.blit(FBD.render("Currently absorbing:",True,WHITE),(cx0+sx(10),by+sy(120)))
    food_in_transit = [d.icon for d in fx_digestion if not d.done][:4]
    bx_ = cx0+sx(160)
    for ico in food_in_transit:
        screen.blit(FICON_MD.render(ico,True,WHITE),(bx_,by+sy(116))); bx_+=sx(30)

    if active_di:
        d = active_di[0]
        pct = d.idx / max(len(d.wpts)-1, 1)
        screen.blit(FSS.render("Progress through GI tract:",True,GREY),(cx0+sx(10),by+sy(145)))
        draw_bar(screen,cx0+sx(10),by+sy(158),mid-sx(20),sy(8),pct*100,100,GUT_COL)

# ═══════════════════════════════════════════════════════════════
#  DRAW: HEADER
# ═══════════════════════════════════════════════════════════════
def draw_header():
    mid_x = LEFT_W + (W-LEFT_W-RIGHT_W)//2
    t = FH.render("Human Body Nutrition Simulator", True, GOLD)
    screen.blit(t,(mid_x-t.get_width()//2, sy(8)))
    sub = FS.render("Drag foods onto organs   Clinically-grounded real-time body response", True, GREY)
    screen.blit(sub,(mid_x-sub.get_width()//2, sy(36)))

# ═══════════════════════════════════════════════════════════════
#  DRAW: DRAG GHOST
# ═══════════════════════════════════════════════════════════════
def draw_drag_card():
    if drag_idx is None: return
    food = FOODS[drag_idx]; col = TRAD if food["kind"]=="trad" else MOD
    cw = CARD_W+10; ch = CARD_H+10
    gr = pygame.Rect(drag_x-cw//2, drag_y-ch//2, cw, ch)
    gs = pygame.Surface((cw,ch), pygame.SRCALPHA)
    bg3 = tuple(c//3 for c in col)
    pygame.draw.rect(gs, bg3,  (0,0,cw,ch), border_radius=11)
    gs.set_alpha(215)
    screen.blit(gs, gr.topleft)
    # Border ring at full opacity
    gb = pygame.Surface((cw,ch), pygame.SRCALPHA)
    pygame.draw.rect(gb, col, (0,0,cw,ch), 2, border_radius=11)
    screen.blit(gb, gr.topleft)
    screen.blit(FICON_XL.render(food["icon"],True,WHITE),(gr.x+5,gr.y+3))
    screen.blit(FCARD.render(food["name"],True,WHITE),(gr.x+4,gr.y+ch-18))

# ═══════════════════════════════════════════════════════════════
#  DRAW: HELP OVERLAY
# ═══════════════════════════════════════════════════════════════
def draw_help():
    if not show_help: return
    ow = sx(680); oh = sy(500)
    ox = (W-ow)//2; oy = (H-oh)//2
    ov = pygame.Surface((ow,oh), pygame.SRCALPHA)
    pygame.draw.rect(ov,(10,12,38),(0,0,ow,oh),border_radius=ss(16))
    ov.set_alpha(248)
    screen.blit(ov,(ox,oy))
    ob = pygame.Surface((ow,oh), pygame.SRCALPHA)
    pygame.draw.rect(ob, GOLD,(0,0,ow,oh),2,border_radius=ss(16))
    ob.set_alpha(200)
    screen.blit(ob,(ox,oy))
    screen.blit(FT.render("Controls & features",True,GOLD),(ox+sx(20),oy+sy(16)))

    cols_data = [
        ("Interactions",
         ["Drag food card onto the body to feed it",
          "Drop on specific organ for targeted effect",
          "Drop anywhere to auto-target nearest organ",
          "Hover food card for full nutritional profile"]),
        ("Keyboard",
         ["1-6 or Tab: switch analysis panels",
          "T: cycle time of day (morning/afternoon/evening)",
          "H: toggle this help overlay",
          "R: reset everything to baseline",
          "Q / Esc: quit"]),
        ("Analysis tabs",
         ["Systems: health meters, glucose, history",
          "Nutrients: 28-nutrient RDA tracker",
          "Gut: microbiome species, digestion stage",
          "Hormones: insulin/cortisol/leptin/ghrelin",
          "Liver: toxin clearance queue & timers",
          "Stats: session report card"]),
        ("Body features",
         ["Organs glow green/red on impact",
          "Organs speak when overloaded",
          "Inflammation heatmap on body",
          "GI tract shows food transit path",
          "Blood glucose curve updates live",
          "Circadian warnings for poor timing"]),
    ]
    cx_ = ox+sx(20); cy_ = oy+sy(50)
    cw2 = (ow-sx(40))//2
    for ci,(title,items) in enumerate(cols_data):
        tx_ = cx_ + (ci%2)*cw2; ty_ = cy_ + (ci//2)*sy(190)
        screen.blit(FB.render(title,True,GOLD),(tx_,ty_)); ty_+=sy(20)
        for item in items:
            screen.blit(FSS.render(f"• {item}",True,LGREY),(tx_,ty_)); ty_+=sy(16)

    cl = FS.render("Press H to close",True,GREY)
    screen.blit(cl,(ox+ow//2-cl.get_width()//2, oy+oh-sy(28)))

# ═══════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════
def main():
    global drag_idx, drag_x, drag_y, hover_food_idx
    global log_scroll, show_help, active_tab, time_of_day

    TOD_CYCLE = ["morning","afternoon","evening"]

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        glucose.update()

        hover_food_idx = None
        if mx < LEFT_W and drag_idx is None:
            for i in range(len(FOODS)):
                if card_rect(i).collidepoint(mx,my):
                    hover_food_idx = i; break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_r: reset_all()
                elif event.key == pygame.K_h: show_help = not show_help
                elif event.key == pygame.K_t:
                    ci = TOD_CYCLE.index(time_of_day)
                    time_of_day = TOD_CYCLE[(ci+1)%3]
                elif event.key == pygame.K_TAB:
                    active_tab = (active_tab+1) % len(TABS)
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    active_tab = event.key - pygame.K_1

            elif event.type == pygame.MOUSEWHEEL:
                ms = max(0, len(effect_log)*LOG_ENTRY_H-(H-380))
                log_scroll = max(0, min(ms, log_scroll-event.y*20))

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                # Tab clicks
                rx2 = W-RIGHT_W
                if rx2 < mx < W and 0 < my < TAB_H:
                    tab_w = RIGHT_W//len(TABS)
                    ti = (mx-rx2)//tab_w
                    if 0 <= ti < len(TABS): active_tab = ti
                elif mx < LEFT_W:
                    for i in range(len(FOODS)):
                        if card_rect(i).collidepoint(mx,my):
                            drag_idx=i; drag_x,drag_y=mx,my; break

            elif event.type == pygame.MOUSEBUTTONUP and event.button==1:
                if drag_idx is not None:
                    if on_body(mx,my):
                        target = organ_at(mx,my)
                        if target is None:
                            target = min(ORGANS.keys(),
                                key=lambda n: math.hypot(mx-organ_world(n)[0],my-organ_world(n)[1]))
                        food = FOODS[drag_idx]
                        ox_,oy_ = organ_world(target)
                        pcol = TRAD if food["kind"]=="trad" else MOD
                        fx_bezier.append(BezierParticle(food["icon"],mx,my,ox_,oy_,pcol))
                        apply_food(food, target)
                    drag_idx = None

            elif event.type == pygame.MOUSEMOTION:
                if drag_idx is not None: drag_x,drag_y = mx,my

        # Update FX
        fx_bezier[:] = [p for p in fx_bezier if p.state!="done"]
        for p in fx_bezier: p.update()
        fx_floats[:] = [f for f in fx_floats if f.life>0]
        for f in fx_floats: f.update()
        for d in fx_digestion: d.update()
        fx_digestion[:] = [d for d in fx_digestion if not d.done or
                           fx_digestion.index(d) < 3]  # keep last 3 for display

        # Draw
        screen.fill(BG)
        draw_body_silhouette()
        draw_gi_tract()
        draw_inflammation_heatmap()
        draw_drop_hints()
        draw_organs()
        for p in fx_bezier: p.draw(screen)
        for f in fx_floats:  f.draw(screen)
        for d in fx_digestion:
            if not d.done: d.draw(screen)
        draw_header()
        draw_food_panel()
        draw_hover_profile()
        draw_right_panel()
        draw_bottom_panel()
        draw_drag_card()
        draw_help()
        pygame.display.flip()

if __name__ == "__main__":
    main()