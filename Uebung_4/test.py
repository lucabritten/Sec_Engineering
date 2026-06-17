import io, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrow
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import HexColor, white, black

# ── Palette ──────────────────────────────────────────────────────────────────
BLUE_DARK  = HexColor("#1a3a5c")
BLUE_MID   = HexColor("#185FA5")
BLUE_LIGHT = HexColor("#B5D4F4")
TEAL       = HexColor("#0F6E56")
TEAL_LIGHT = HexColor("#9FE1CB")
AMBER      = HexColor("#BA7517")
AMBER_LIGHT= HexColor("#FAC775")
CORAL      = HexColor("#993C1D")
CORAL_LIGHT= HexColor("#F5C4B3")
GRAY_DARK  = HexColor("#444441")
GRAY_MID   = HexColor("#888780")
GRAY_LIGHT = HexColor("#F1EFE8")
RED        = HexColor("#A32D2D")
RED_LIGHT  = HexColor("#F7C1C1")
WHITE      = white
PAGE_W, PAGE_H = A4

# ── Helper: matplotlib figure → ReportLab Image ──────────────────────────────
def fig_to_rl_image(fig, width_cm=16):
    buf = io.BytesIO()

    # Originalgröße der Matplotlib-Figur ermitteln
    fig_w, fig_h = fig.get_size_inches()
    aspect = fig_h / fig_w

    fig.savefig(
        buf,
        format="png",
        dpi=150,
        bbox_inches="tight",
        facecolor=fig.get_facecolor()
    )
    buf.seek(0)
    plt.close(fig)

    w = width_cm * cm
    h = w * aspect

    img = Image(buf, width=w, height=h)
    img.hAlign = "CENTER"
    return img

# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}
    s["title_page"] = ParagraphStyle("title_page", parent=base["Title"],
        fontSize=26, textColor=WHITE, leading=32, spaceAfter=6,
        fontName="Helvetica-Bold")
    s["subtitle_page"] = ParagraphStyle("subtitle_page", parent=base["Normal"],
        fontSize=13, textColor=HexColor("#B5D4F4"), leading=18,
        fontName="Helvetica")
    s["h1"] = ParagraphStyle("h1", parent=base["Heading1"],
        fontSize=16, textColor=BLUE_DARK, fontName="Helvetica-Bold",
        spaceBefore=18, spaceAfter=6, borderPad=0,
        borderColor=BLUE_MID, borderWidth=0)
    s["h2"] = ParagraphStyle("h2", parent=base["Heading2"],
        fontSize=12, textColor=BLUE_MID, fontName="Helvetica-Bold",
        spaceBefore=12, spaceAfter=4)
    s["body"] = ParagraphStyle("body", parent=base["Normal"],
        fontSize=10, leading=15, textColor=GRAY_DARK,
        fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=6)
    s["bullet"] = ParagraphStyle("bullet", parent=base["Normal"],
        fontSize=10, leading=14, textColor=GRAY_DARK,
        fontName="Helvetica", leftIndent=14, spaceAfter=3,
        bulletIndent=4)
    s["caption"] = ParagraphStyle("caption", parent=base["Normal"],
        fontSize=8.5, leading=12, textColor=GRAY_MID,
        fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=10)
    s["code"] = ParagraphStyle("code", parent=base["Normal"],
        fontSize=8.5, leading=13, textColor=HexColor("#2C2C2A"),
        fontName="Courier", leftIndent=10, backgroundColor=GRAY_LIGHT,
        borderPad=6)
    s["tag_p1"] = ParagraphStyle("tag_p1", parent=base["Normal"],
        fontSize=9, fontName="Helvetica-Bold", textColor=WHITE,
        alignment=TA_CENTER)
    s["note"] = ParagraphStyle("note", parent=base["Normal"],
        fontSize=9, leading=13, textColor=HexColor("#185FA5"),
        fontName="Helvetica-Oblique", leftIndent=8)
    return s

# ── Cover page background ─────────────────────────────────────────────────────
class CoverBackground(Flowable):
    def draw(self):
        c = self.canv
        c.setFillColor(BLUE_DARK)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.setFillColor(BLUE_MID)
        c.rect(0, PAGE_H*0.38, PAGE_W, PAGE_H*0.62, fill=1, stroke=0)
        c.setFillColor(HexColor("#0d2d47"))
        c.rect(0, 0, PAGE_W, PAGE_H*0.38, fill=1, stroke=0)
        # accent stripe
        c.setFillColor(TEAL)
        c.rect(0, PAGE_H*0.38-4*mm, PAGE_W, 4*mm, fill=1, stroke=0)
    def wrap(self, aw, ah): return (0, 0)

# ── Colored box flowable ──────────────────────────────────────────────────────
class ColorBox(Flowable):
    def __init__(self, text, bg, fg=WHITE, height=22, radius=4, style=None):
        self.text = text; self.bg = bg; self.fg = fg
        self.height = height; self.radius = radius; self.style = style
    def wrap(self, aw, ah):
        self._w = aw
        return (aw, self.height + 4)
    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self._w, self.height, self.radius, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(self._w/2, self.height/2 - 4, self.text)

# ── Section rule ─────────────────────────────────────────────────────────────
def section_rule():
    return HRFlowable(width="100%", thickness=1.5, color=BLUE_MID,
                      spaceAfter=4, spaceBefore=2)

# ════════════════════════════════════════════════════════════════════════════
# FIGURES
# ════════════════════════════════════════════════════════════════════════════

def fig_system_overview():
    """Five-layer architecture with data flows."""
    fig, ax = plt.subplots(figsize=(13, 6.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 13); ax.set_ylim(0, 6.5)
    ax.axis("off")

    layers = [
        ("Aktor-Ebene",       "#1a3a5c", "#B5D4F4", 0.0,  1.2, ["Mensch", "UR-Roboter"]),
        ("Sensor-Ebene",      "#0F6E56", "#9FE1CB", 1.4,  1.2, ["EEG", "ECG/SpO₂", "Kamera", "Temp"]),
        ("Verarbeitungs-Ebene","#185FA5","#E6F1FB", 2.8,  1.2, ["Vorverarbeitung A", "Vorverarbeitung B", "DataHub"]),
        ("Assistenz-Ebene",   "#BA7517", "#FAEEDA", 4.2,  1.2, ["Aufmerksamkeits-\nassistent", "Triage-Engine"]),
        ("Informations-Ebene","#993C1D", "#FAECE7", 5.6,  1.2, ["Mixed Reality", "Haptikweste", "Display"]),
    ]

    for name, fc, lc, y0, h, nodes in layers:
        rect = FancyBboxPatch((0.15, y0+0.08), 12.7, h-0.16,
                              boxstyle="round,pad=0.08", linewidth=1.2,
                              edgecolor=fc, facecolor=lc+"44" if len(lc)==7 else lc)
        ax.add_patch(rect)
        ax.text(0.38, y0+h/2, name, fontsize=8.5, fontweight="bold",
                color=fc, va="center", rotation=0)

        n = len(nodes)
        xs = np.linspace(2.5, 12.2, n)
        for xi, nd in zip(xs, nodes):
            box = FancyBboxPatch((xi-0.85, y0+0.22), 1.7, h-0.44,
                                 boxstyle="round,pad=0.06", linewidth=0.8,
                                 edgecolor=fc, facecolor=fc)
            ax.add_patch(box)
            ax.text(xi, y0+h/2, nd, fontsize=7.5, color="white",
                    ha="center", va="center", fontweight="bold",
                    multialignment="center")

    # vertical arrows between layers
    arrow_kw = dict(arrowstyle="->", color="#444441", lw=1.2,
                    connectionstyle="arc3,rad=0")
    for yi in [1.2, 2.4, 3.6, 4.8]:
        ax.annotate("", xy=(6.5, yi+1.4-0.08), xytext=(6.5, yi+0.08),
                    arrowprops=dict(arrowstyle="->", color="#888780", lw=1.0))

    # back-channel arrow (triage commands)
    ax.annotate("", xy=(1.5, 5.6+0.6), xytext=(1.5, 2.8+0.6),
                arrowprops=dict(arrowstyle="->", color="#A32D2D", lw=1.5,
                                linestyle="dashed",
                                connectionstyle="arc3,rad=-0.35"))
    ax.text(0.18, 4.5, "Triage-\nKommandos", fontsize=7, color="#A32D2D",
            ha="center", fontstyle="italic")

    ax.set_title("Systemarchitektur ResCom – fünf Ebenen mit Triage-Rückkanal",
                 fontsize=10, pad=8, color="#1a3a5c", fontweight="bold")
    fig.tight_layout(pad=0.4)
    return fig


def fig_triage_state_machine():
    """State machine: Normal → Warning → Critical → Emergency."""
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(0, 4)
    ax.axis("off")

    states = [
        (1.4, 2.0, "Normal\n< 60%",   "#0F6E56", "#9FE1CB"),
        (4.0, 2.0, "Warning\n60–75%", "#BA7517", "#FAC775"),
        (7.0, 2.0, "Critical\n75–90%","#993C1D", "#F5C4B3"),
        (10.2,2.0, "Emergency\n> 90%","#A32D2D", "#F7C1C1"),
    ]
    r = 0.9
    for x, y, label, fc, lc in states:
        circ = plt.Circle((x, y), r, color=lc, ec=fc, lw=2, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y, label, ha="center", va="center", fontsize=8.5,
                fontweight="bold", color=fc, zorder=4, multialignment="center")

    transitions = [
        (1.4+r, 4.0-r, 4.0-r, 4.0-r, "BW > 60%\nP3 drosseln"),
        (4.0+r, 7.0-r, 4.0-r, 4.0-r, "BW > 75%\nP2 ↓25%"),
        (7.0+r, 10.2-r,4.0-r, 4.0-r, "BW > 90%\nnur P1"),
    ]
    for x1, x2, y1, y2, label in transitions:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#444441", lw=1.5))
        mx = (x1+x2)/2
        ax.text(mx, y1+0.28, label, ha="center", va="bottom",
                fontsize=7, color="#444441", multialignment="center")

    # recovery arrows (below)
    rec = [
        (4.0-r, 1.4+r, "BW < 55%\nrestore P3"),
        (7.0-r, 4.0+r, "BW < 70%\nrestore P2"),
        (10.2-r,7.0+r, "BW < 85%\nrestore P1"),
    ]
    for x1, x2, label in rec:
        y = 2.0-r-0.1
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color="#185FA5", lw=1.2,
                                   connectionstyle="arc3,rad=0.4"))
        mx = (x1+x2)/2
        ax.text(mx, y-0.55, label, ha="center", va="top",
                fontsize=7, color="#185FA5", multialignment="center")

    ax.set_title("Triage-Zustandsautomat – Übergänge und Wiederherstellung",
                 fontsize=10, pad=6, color="#1a3a5c", fontweight="bold")
    fig.tight_layout(pad=0.4)
    return fig


def fig_priority_streams():
    """Bar chart showing stream properties with priority color."""
    fig, ax = plt.subplots(figsize=(11, 4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#F8F8F6")

    streams = ["EEG\n500 Hz", "ECG\n250 Hz", "SpO₂\n50 Hz",
               "Kamera\n30 fps", "Hauttemp\n1 Hz", "Produktions-\ndaten"]
    bw      = [4.0, 1.0, 0.2, 12.0, 0.01, 0.5]   # relative BW (arbitrary)
    prios   = ["P1","P1","P1","P2","P3","P3"]
    cols    = {"P1":"#1a3a5c","P2":"#BA7517","P3":"#888780"}
    bar_cols = [cols[p] for p in prios]

    bars = ax.bar(streams, bw, color=bar_cols, edgecolor="white",
                  linewidth=0.8, width=0.6)
    for bar, prio, val in zip(bars, prios, bw):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.15,
                prio, ha="center", va="bottom", fontsize=9,
                fontweight="bold", color=cols[prio])

    ax.set_ylabel("Relative Bandbreite (normiert)", fontsize=9, color="#444441")
    ax.set_title("Streams nach Priorität und Bandbreitenbedarf",
                 fontsize=10, color="#1a3a5c", fontweight="bold", pad=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors="#444441", labelsize=8.5)
    ax.set_ylim(0, 14)

    legend_patches = [
        mpatches.Patch(color=cols["P1"], label="P1 – immer senden (Echtzeit-kritisch)"),
        mpatches.Patch(color=cols["P2"], label="P2 – Rate drosseln bei Engpass"),
        mpatches.Patch(color=cols["P3"], label="P3 – pausieren / Store-and-Forward"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="upper right",
              framealpha=0.9, edgecolor="#cccccc")
    fig.tight_layout(pad=0.5)
    return fig


def fig_bandwidth_monitor():
    """Time-series: bandwidth utilization with triage events."""
    t = np.linspace(0, 60, 600)
    # synthetic load curve
    bw = (0.4 + 0.15*np.sin(0.3*t)
          + 0.25*np.exp(-((t-20)**2)/18)
          + 0.35*np.exp(-((t-38)**2)/10)
          + 0.12*np.random.default_rng(42).standard_normal(600).cumsum()*0.004)
    bw = np.clip(bw, 0, 1)

    fig, ax = plt.subplots(figsize=(12, 3.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # zones
    ax.axhspan(0,    0.60, facecolor="#EAF3DE", alpha=0.5)
    ax.axhspan(0.60, 0.75, facecolor="#FAEEDA", alpha=0.5)
    ax.axhspan(0.75, 0.90, facecolor="#FAECE7", alpha=0.5)
    ax.axhspan(0.90, 1.00, facecolor="#FCEBEB", alpha=0.6)

    ax.axhline(0.60, color="#639922", ls="--", lw=0.9, label="Warning (60%)")
    ax.axhline(0.75, color="#BA7517", ls="--", lw=0.9, label="Critical (75%)")
    ax.axhline(0.90, color="#A32D2D", ls="--", lw=0.9, label="Emergency (90%)")

    ax.plot(t, bw, color="#185FA5",
            lw=1.6, label="Bandbreitenauslastung")

    # annotate triage events
    for tx, ty, label, col in [
        (20, 0.85, "P3 pausiert", "#993C1D"),
        (38, 0.93, "P2 gedrosselt\n+ P3 pausiert", "#A32D2D"),
        (48, 0.55, "Wiederherstellung\naller Streams", "#0F6E56"),
    ]:
        ax.annotate(label, xy=(tx, ty), xytext=(tx+3, ty+0.06),
                    fontsize=7.5, color=col,
                    arrowprops=dict(arrowstyle="->", color=col, lw=0.8),
                    multialignment="center")

    ax.set_xlabel("Zeit (s)", fontsize=9, color="#444441")
    ax.set_ylabel("Auslastung", fontsize=9, color="#444441")
    ax.set_title("Ressourcenmonitor – Bandbreitenauslastung mit Triage-Ereignissen",
                 fontsize=10, color="#1a3a5c", fontweight="bold", pad=6)
    ax.set_ylim(0, 1.08)
    ax.legend(fontsize=8, loc="upper left", framealpha=0.9, edgecolor="#cccccc")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors="#444441", labelsize=8.5)
    fig.tight_layout(pad=0.4)
    return fig


def fig_bottleneck_simulation():
    """Two methods side by side: tc netem vs traffic injector."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2))
    fig.patch.set_facecolor("white")

    for ax in (ax1, ax2):
        ax.set_facecolor("white")
        ax.axis("off")
        ax.set_xlim(0, 6); ax.set_ylim(0, 4.5)

    # --- ax1: tc netem ---
    ax1.set_title("Methode 1: tc netem (Kernel-Level)", fontsize=9,
                  fontweight="bold", color="#1a3a5c", pad=4)
    boxes1 = [
        (0.3, 3.2, 2.0, 0.8, "#1a3a5c", "Anwendung\n(LSL Outlet)"),
        (0.3, 1.9, 2.0, 0.8, "#BA7517", "tc netem\nBW-Limit + Delay"),
        (0.3, 0.6, 2.0, 0.8, "#0F6E56", "Netzwerk-\ninterface"),
        (3.3, 1.9, 2.2, 0.8, "#185FA5", "Empfänger\n(DataHub)"),
    ]
    for x, y, w, h, c, label in boxes1:
        r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                           facecolor=c, edgecolor="white", lw=1.2)
        ax1.add_patch(r)
        ax1.text(x+w/2, y+h/2, label, ha="center", va="center",
                 fontsize=7.5, color="white", fontweight="bold",
                 multialignment="center")
    for y1, y2 in [(3.2, 2.7), (1.9, 1.5)]:
        ax1.annotate("", xy=(1.3, y2), xytext=(1.3, y1),
                     arrowprops=dict(arrowstyle="->", color="#444441", lw=1.2))
    ax1.annotate("", xy=(3.3+0.1, 2.3), xytext=(2.3, 2.3),
                 arrowprops=dict(arrowstyle="->", color="#888780", lw=1.2,
                                 linestyle="dashed"))
    ax1.text(2.8, 2.45, "gedrosselt", ha="center", fontsize=7,
             color="#888780", fontstyle="italic")
    ax1.text(0.2, 0.1,
             "sudo tc qdisc add dev eth0\n  root netem rate 5mbit delay 20ms",
             fontsize=6.8, color="#2C2C2A", fontfamily="monospace",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#F1EFE8", edgecolor="#cccccc"))

    # --- ax2: traffic injector ---
    ax2.set_title("Methode 2: Traffic-Injektor (Software)", fontsize=9,
                  fontweight="bold", color="#1a3a5c", pad=4)
    boxes2 = [
        (0.2, 3.2, 2.0, 0.8, "#1a3a5c", "ResCom\nStreams (P1/P2/P3)"),
        (3.3, 3.2, 2.2, 0.8, "#185FA5", "DataHub"),
        (0.2, 1.5, 2.0, 0.8, "#A32D2D", "Traffic-\nInjektor (UDP)"),
    ]
    for x, y, w, h, c, label in boxes2:
        r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                           facecolor=c, edgecolor="white", lw=1.2)
        ax2.add_patch(r)
        ax2.text(x+w/2, y+h/2, label, ha="center", va="center",
                 fontsize=7.5, color="white", fontweight="bold",
                 multialignment="center")

    ax2.annotate("", xy=(3.3, 3.6), xytext=(2.2, 3.6),
                 arrowprops=dict(arrowstyle="->", color="#444441", lw=1.2))
    ax2.annotate("", xy=(3.4, 3.2), xytext=(1.2, 2.3),
                 arrowprops=dict(arrowstyle="->", color="#A32D2D", lw=1.2,
                                 linestyle="dotted",
                                 connectionstyle="arc3,rad=-0.25"))
    ax2.text(2.6, 2.6, "Dummy-Traffic\n(vorbelasten)", ha="center",
             fontsize=7, color="#A32D2D", fontstyle="italic",
             multialignment="center")

    # load steps
    for i, (load, col) in enumerate([(20,"#639922"),(50,"#BA7517"),
                                      (80,"#A32D2D"),(0,"#0F6E56")]):
        ax2.text(0.3 + i*1.35, 0.9, f"{load}%", ha="center",
                 fontsize=8, fontweight="bold", color=col)
        ax2.text(0.3 + i*1.35, 0.5, f"Stufe {i+1}", ha="center",
                 fontsize=7, color="#888780")
    ax2.text(2.8, 1.18, "schrittweise Last →", ha="center",
             fontsize=7, color="#444441")

    fig.suptitle("Methoden zur Engpass-Simulation", fontsize=10,
                 fontweight="bold", color="#1a3a5c", y=1.01)
    fig.tight_layout(pad=0.6)
    return fig


def fig_store_forward():
    """Timeline showing store-and-forward buffering."""
    fig, ax = plt.subplots(figsize=(12, 3.6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 12); ax.set_ylim(-0.5, 3.5)
    ax.axis("off")

    # time axis
    ax.arrow(0.3, 0, 11.4, 0, head_width=0.08, head_length=0.15,
             fc="#444441", ec="#444441", lw=1.2)
    ax.text(11.9, -0.05, "Zeit", fontsize=8.5, va="center", color="#444441")

    # phases
    phases = [
        (0.4, 3.5, "#E6F1FB", "#185FA5", "Normal\n(alle Streams aktiv)"),
        (3.9, 4.0, "#FAECE7", "#993C1D", "Engpass\n(P3 pausiert, P2 gedrosselt)"),
        (8.3, 3.2, "#EAF3DE", "#0F6E56", "Erholung\n(Backlog wird abgebaut)"),
    ]
    for x0, w, fc, ec, label in phases:
        r = FancyBboxPatch((x0, 0.3), w, 2.8, boxstyle="round,pad=0.1",
                           facecolor=fc, edgecolor=ec, lw=1.2, alpha=0.7)
        ax.add_patch(r)
        ax.text(x0+w/2, 2.8, label, ha="center", va="top",
                fontsize=7.5, color=ec, fontweight="bold",
                multialignment="center")

    # stream rows
    rows = [
        (2.4, "P1  EEG/ECG", "#1a3a5c", [(0.4,11.5)]),
        (1.6, "P2  Kamera",  "#BA7517",
              [(0.4,3.9),(8.3,11.5)], [(3.9,8.3,"Buffer/Disk")]),
        (0.8, "P3  Temp",    "#888780",
              [(0.4,3.9),(8.3,11.5)], [(3.9,8.3,"Buffer/Disk")]),
    ]
    for y, label, col, active_segs, *paused in rows:
        ax.text(0.35, y, label, ha="right", va="center",
                fontsize=7.5, color=col, fontweight="bold")
        for x0, x1 in active_segs:
            ax.plot([x0, x1], [y, y], color=col, lw=5, solid_capstyle="round",
                    alpha=0.85)
        if paused:
            for x0, x1, lbl in paused[0]:
                ax.plot([x0, x1], [y, y], color=col, lw=5,
                        solid_capstyle="round", alpha=0.25)
                ax.text((x0+x1)/2, y+0.22, lbl, ha="center",
                        fontsize=6.5, color=col, fontstyle="italic")

    # original-timestamp label
    ax.annotate("Orig. Timestamps\nerhalten → Re-Sync im DataHub",
                xy=(9.5, 1.2), xytext=(9.5, 3.3),
                fontsize=7, color="#0F6E56",
                ha="center", multialignment="center",
                arrowprops=dict(arrowstyle="->", color="#0F6E56", lw=0.9))

    ax.set_title("Store-and-Forward – Puffer-Verhalten bei Engpass",
                 fontsize=10, color="#1a3a5c", fontweight="bold", pad=6)
    fig.tight_layout(pad=0.4)
    return fig


# ════════════════════════════════════════════════════════════════════════════
# BUILD PDF
# ════════════════════════════════════════════════════════════════════════════

def build():
    out = "ResCom_Ressourcensensitivitaet_Konzept.pdf"
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
    )
    S = make_styles()
    story = []

    # ── Cover ────────────────────────────────────────────────────────────────
    story.append(CoverBackground())
    story.append(Spacer(1, 4.2*cm))
    story.append(Paragraph("ResCom", S["title_page"]))
    story.append(Paragraph("Ressourcensensitive Kommunikation", S["title_page"]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "Konzept: Triage-basiertes Ressourcenmanagement für verteilte "
        "Echtzeit-Datenströme in Industrie-4.0-Szenarien",
        S["subtitle_page"]))
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph(
        "htw saar · Embedded Robotics Lab · FH-Kooperativ",
        S["subtitle_page"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Konzeptpapier zur internen Diskussion · 2025",
                            S["subtitle_page"]))
    story.append(PageBreak())

    # ── 1 Motivation ─────────────────────────────────────────────────────────
    story.append(Paragraph("1  Motivation und Problemstellung", S["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Das ResCom-Projekt zielt auf die Echtzeitfusion psychophysiologischer "
        "Daten (EEG, ECG, SpO₂, Kamera) mit Maschinen- und Produktionsdaten in "
        "einem Industrie-4.0-Szenario. Bisherige Kommunikationstechnologien im "
        "M4P-Lab sind <b>nicht ressourcensensitiv</b>: Sie passen ihre Senderate "
        "nicht dynamisch an verfügbare Ressourcen an und können bei Engpässen "
        "zu unkontrolliertem, unpriorisiertem Paketverlust führen.",
        S["body"]))
    story.append(Paragraph(
        "Dieses Konzept beschreibt einen <b>Triage-basierten Ansatz</b>, der "
        "folgende Anforderungen erfüllt:", S["body"]))

    reqs = [
        ("R1", BLUE_MID,  "Priorisierung von Streams nach Echtzeitkritikalität (P1 > P2 > P3)"),
        ("R2", TEAL,      "Dynamische Anpassung von Senderaten und Pausierung bei Ressourcenengpässen"),
        ("R3", AMBER,     "Store-and-Forward-Puffer für nicht-Echtzeit-kritische Datenquellen"),
        ("R4", CORAL,     "Rückkanal für Triage-Kommandos vom DataHub zu den Sensorknoten"),
        ("R5", BLUE_DARK, "Simulierbarkeit von Engpässen für Testzwecke"),
    ]
    tdata = []
    for code, col, text in reqs:
        tdata.append([
            Paragraph(f"<b>{code}</b>", ParagraphStyle("rc", parent=S["body"],
                      textColor=WHITE, alignment=TA_CENTER, fontSize=9)),
            Paragraph(text, S["body"]),
        ])
    t = Table(tdata, colWidths=[1.1*cm, 14.2*cm])
    tstyle = TableStyle([
        ("BACKGROUND", (0,0), (0,-1), BLUE_MID),
        ("TEXTCOLOR",  (0,0), (0,-1), WHITE),
        ("ALIGN",      (0,0), (0,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (1,0), (1,-1), [GRAY_LIGHT, WHITE]),
        ("BOX",        (0,0), (-1,-1), 0.5, GRAY_MID),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, GRAY_MID),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0), (-1,-1), 6),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ])
    # color code column per row
    row_cols = [BLUE_MID, TEAL, AMBER, CORAL, BLUE_DARK]
    for i, col in enumerate(row_cols):
        tstyle.add("BACKGROUND", (0,i), (0,i), col)
    t.setStyle(tstyle)
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # ── 2 Systemarchitektur ──────────────────────────────────────────────────
    story.append(Paragraph("2  Systemarchitektur", S["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Die Architektur des ResCom-Demonstrators gliedert sich in fünf "
        "hierarchische Ebenen (vgl. Zwischenbericht 2025). Das Ressourcenmanagement "
        "ergänzt diese Architektur um einen <b>Triage-Rückkanal</b>, über den der "
        "DataHub Kommandos an Sensorknoten senden kann.", S["body"]))
    story.append(fig_to_rl_image(fig_system_overview(), 15.5))
    story.append(Paragraph(
        "Abb. 1: Fünf-Ebenen-Architektur mit Triage-Rückkanal (gestrichelt rot). "
        "Der DataHub in der Verarbeitungsebene koordiniert alle Ressourcenentscheidungen.",
        S["caption"]))

    story.append(Paragraph("2.1  Datenquellen und Prioritäten", S["h2"]))
    story.append(Paragraph(
        "Jeder Stream erhält beim Start einen Prioritäts-Tag in den "
        "LSL-Metadaten. Die Tabelle zeigt die vorgesehene Klassifikation:", S["body"]))

    stream_data = [
        ["Stream", "Rate", "Technologie", "Prio", "Triage-Verhalten"],
        ["EEG",         "500 Hz",  "BLE",      "P1", "Immer senden"],
        ["ECG / SpO₂",  "250 Hz",  "BLE",      "P1", "Immer senden"],
        ["Kamera",      "30 fps",  "Wi-Fi",    "P2", "Rate ↓ 50 % → 10 % → Pause"],
        ["Hauttemperatur","1 Hz",  "BLE",      "P3", "Pause + Store-and-Forward"],
        ["Produktionsdaten","variabel","TCP/IP","P3", "Store-and-Forward (Disk)"],
        ["Datenbank-Updates","selten","TCP/IP", "P3", "Store-and-Forward (Disk)"],
    ]
    st = Table(stream_data, colWidths=[3.2*cm, 2.0*cm, 2.4*cm, 1.4*cm, 6.3*cm])
    hcol = BLUE_DARK
    st.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), hcol),
        ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GRAY_LIGHT, WHITE]),
        ("BACKGROUND",  (3,1),(3,2), HexColor("#E6F1FB")),
        ("BACKGROUND",  (3,3),(3,3), HexColor("#FAEEDA")),
        ("BACKGROUND",  (3,4),(3,-1),HexColor("#F1EFE8")),
        ("TEXTCOLOR",   (3,1),(3,2), BLUE_DARK),
        ("TEXTCOLOR",   (3,3),(3,3), AMBER),
        ("TEXTCOLOR",   (3,4),(3,-1),GRAY_DARK),
        ("FONTNAME",    (3,1),(3,-1),"Helvetica-Bold"),
        ("BOX",         (0,0),(-1,-1),0.5, GRAY_MID),
        ("INNERGRID",   (0,0),(-1,-1),0.3, GRAY_MID),
        ("ALIGN",       (3,0),(3,-1),"CENTER"),
        ("VALIGN",      (0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING", (0,0),(-1,-1),5),
        ("TOPPADDING",  (0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.2*cm))
    story.append(fig_to_rl_image(fig_priority_streams(), 14))
    story.append(Paragraph(
        "Abb. 2: Relative Bandbreitenanforderungen der Streams nach Priorität. "
        "Die Kamera dominiert den Bedarf und ist damit primäres Drosselungsziel.",
        S["caption"]))

    # ── 3 Ressourcenmonitor ──────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("3  Ressourcenmonitor", S["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Der Ressourcenmonitor ist ein eigenständiges Modul innerhalb des DataHub, "
        "das kontinuierlich Bandbreite, CPU-Last und RAM-Auslastung des Systems "
        "abfragt und bei Überschreitung definierter Schwellenwerte den "
        "Triage-Zustandsautomaten auslöst.", S["body"]))

    story.append(Paragraph("3.1  Überwachte Metriken", S["h2"]))
    metric_data = [
        ["Metrik", "Quelle", "Abfrage-Intervall", "Auflösung"],
        ["Netzwerk-TX-Rate","psutil.net_io_counters()","100 ms","Bytes/s"],
        ["CPU-Auslastung","psutil.cpu_percent()","500 ms","Prozent"],
        ["RAM-Nutzung","psutil.virtual_memory()","500 ms","Prozent"],
        ["LSL-Buffer-Füllstand","inlet.samples_available()","50 ms","Samples"],
        ["Paketloss (UDP)","Socket-Statistik","1 s","Prozent"],
    ]
    mt = Table(metric_data, colWidths=[4.5*cm, 4.5*cm, 3.0*cm, 3.3*cm])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), BLUE_MID),
        ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GRAY_LIGHT, WHITE]),
        ("BOX",        (0,0),(-1,-1),0.5, GRAY_MID),
        ("INNERGRID",  (0,0),(-1,-1),0.3, GRAY_MID),
        ("VALIGN",     (0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING", (0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3.2  Triage-Zustandsautomat", S["h2"]))
    story.append(Paragraph(
        "Vier Zustände steuern das Verhalten aller Streams. "
        "Übergänge werden durch Schwellenwerte der Bandbreitenauslastung ausgelöst; "
        "Hysterese verhindert schnelles Hin- und Herschalten:", S["body"]))
    story.append(fig_to_rl_image(fig_triage_state_machine(), 15.5))
    story.append(Paragraph(
        "Abb. 3: Triage-Zustandsautomat. Blaue Pfeile unten zeigen den Wiederherstellungspfad "
        "mit Hysterese (Recovery-Schwelle liegt 5 Prozentpunkte unterhalb der Auslöseschwelle).",
        S["caption"]))

    story.append(fig_to_rl_image(fig_bandwidth_monitor(), 15.5))
    story.append(Paragraph(
        "Abb. 4: Synthetische Bandbreitenauslastung mit automatischen Triage-Ereignissen. "
        "Farbige Zonen entsprechen den vier Systemzuständen.",
        S["caption"]))

    # ── 4 Triage-Engine ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4  Triage-Engine und Rückkanal", S["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Die Triage-Engine setzt die Entscheidungen des Zustandsautomaten in "
        "konkrete Kommandos um. Diese werden über einen <b>Rückkanal</b> an die "
        "jeweiligen Sensorknoten übermittelt, die daraufhin ihre Sendeschleife "
        "anpassen.", S["body"]))

    story.append(Paragraph("4.1  Rückkanaloptionen", S["h2"]))
    chan_data = [
        ["Option", "Mechanismus", "Vorteil", "Nachteil"],
        ["A – LSL Control Stream",
         "DataHub öffnet eigenen LSL-Outlet mit IRREGULAR_RATE",
         "Bleibt vollständig im LSL-Ökosystem, keine zusätzliche Abhängigkeit",
         "Polling nötig; keine garantierte Zustellung"],
        ["B – REST/HTTP (FastAPI)",
         "POST /control/rate an Sensorknoten-Server",
         "Einfach debuggbar, klare API; Standard HTTP-Fehlerbehandlung",
         "Zusätzlicher Server auf jedem Knoten; TCP-Overhead"],
        ["C – MQTT",
         "Broker-Topic pro Stream, QoS 1",
         "Garantierte Zustellung; gut für viele Knoten skalierbar",
         "Broker als Single Point of Failure; mehr Setup"],
    ]
    ct = Table(chan_data, colWidths=[2.6*cm, 4.0*cm, 4.2*cm, 4.5*cm])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), TEAL),
        ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GRAY_LIGHT, WHITE]),
        ("BOX",        (0,0),(-1,-1),0.5, GRAY_MID),
        ("INNERGRID",  (0,0),(-1,-1),0.3, GRAY_MID),
        ("VALIGN",     (0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING", (0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("WORDWRAP",   (0,0),(-1,-1),"CJK"),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<b>Empfehlung für ResCom:</b> Option A als Einstiegspunkt "
        "(minimaler Mehraufwand), Option B sobald Debugging und Logging wichtiger werden.",
        S["note"]))

    story.append(Paragraph("4.2  Throttle-Logik auf dem Sensorknoten", S["h2"]))
    story.append(Paragraph(
        "Jeder Sensorknoten führt eine steuerbare Sendeschleife. "
        "LSL selbst bietet keine dynamische Ratenanpassung – "
        "die Kontrolle liegt vollständig in der Applikationsschicht:", S["body"]))

    code_text = (
        "class ThrottleableSensor:\n"
        "    def set_rate(self, hz):          # hz=0 → pausieren\n"
        "        self.paused = (hz == 0)\n"
        "        self.current_rate = hz\n\n"
        "    def run(self, sample_fn):\n"
        "        while True:\n"
        "            if self.paused:\n"
        "                time.sleep(0.05); continue\n"
        "            self.outlet.push_sample(sample_fn())\n"
        "            time.sleep(1.0 / self.current_rate)"
    )
    story.append(Paragraph(code_text.replace("\n","<br/>").replace(" ","&nbsp;"),
                            S["code"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Hinweis: Bei BLE-Geräten mit fest einprogrammierter Firmware-Rate "
        "(z.B. manche Polar-Sensoren) ist nur empfängerseitiges Sub-Sampling möglich. "
        "Geräte mit SDK (Shimmer, eigene Hardware) können die Rate auf Treiberebene setzen.",
        S["note"]))

    # ── 5 Store-and-Forward ──────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("5  Store-and-Forward für nicht-Echtzeit-Daten", S["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Datenquellen mit Priorität P2/P3, die nicht live für den "
        "Aufmerksamkeitsassistenten benötigt werden, können bei Engpässen "
        "lokal gepuffert und nach Entlastung des Netzes mit ihren "
        "<b>originalen Timestamps</b> nachgesendet werden. "
        "Der DataHub kann die Daten damit korrekt in der ALM zeitlich einordnen.", S["body"]))

    story.append(fig_to_rl_image(fig_store_forward(), 15.5))
    story.append(Paragraph(
        "Abb. 5: Store-and-Forward-Verhalten bei einem Engpass. P1-Streams "
        "laufen durchgehend; P2/P3-Streams puffern lokal und werden nach der "
        "Erholung mit originalen Zeitstempeln nachgesendet.",
        S["caption"]))

    story.append(Paragraph("5.1  Buffer-Hierarchie", S["h2"]))
    story.append(Paragraph(
        "Zwei Pufferstufen fangen unterschiedlich lange Engpässe ab:", S["body"]))

    buf_data = [
        ["Stufe", "Speicher", "Kapazität (Beispiel)", "Geeignet für"],
        ["1 – RAM-Ring",  "deque(maxlen=N)", "~50 000 Samples ≈ 100 s@500Hz", "Kurze Engpässe (< 2 min)"],
        ["2 – Disk-Spill","JSON / SQLite",   "Begrenzt durch Speicher", "Lange Engpässe, Sitzungsarchiv"],
    ]
    bt = Table(buf_data, colWidths=[2.6*cm, 3.2*cm, 4.8*cm, 4.7*cm])
    bt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), AMBER),
        ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GRAY_LIGHT, WHITE]),
        ("BOX",        (0,0),(-1,-1),0.5, GRAY_MID),
        ("INNERGRID",  (0,0),(-1,-1),0.3, GRAY_MID),
        ("VALIGN",     (0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING", (0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(bt)
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph(
        "Wichtig: Für den Aufmerksamkeitsassistenten (Live-Feedback, Roboterstopp) "
        "dürfen <b>ausschließlich aktuelle P1-Daten</b> verwendet werden. "
        "Nachgereichte P2/P3-Daten fließen nur in die ALM-Rekonstruktion und "
        "Offline-Analyse ein.", S["note"]))

    # ── 6 Engpass-Simulation ──────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("6  Simulation von Ressourcenengpässen", S["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Damit die Triage-Logik reproduzierbar getestet werden kann, "
        "müssen Engpässe kontrolliert induziert werden. "
        "Zwei komplementäre Methoden werden vorgeschlagen:", S["body"]))

    story.append(fig_to_rl_image(fig_bottleneck_simulation(), 15.5))
    story.append(Paragraph(
        "Abb. 6: Methode 1 (Kernel-Level via tc netem) und Methode 2 (Software-Injektor). "
        "Beide Methoden lassen sich kombinieren für vollständige Systemtests.",
        S["caption"]))

    story.append(Paragraph("6.1  Methode 1: tc netem (empfohlen)", S["h2"]))
    story.append(Paragraph(
        "Das Linux-Kernel-Modul <i>netem</i> ermöglicht präzise Netzwerkbeschränkungen "
        "ohne Applikationsänderungen. Es wirkt auf Netzwerkinterface-Ebene und "
        "beeinflusst alle darüber laufenden Verbindungen:", S["body"]))

    tc_code = (
        "# Bandbreite auf 5 Mbit/s + 20 ms Latenz begrenzen\n"
        "sudo tc qdisc add dev eth0 root netem \\\n"
        "    rate 5mbit delay 20ms 5ms distribution normal\n\n"
        "# Paketverlust von 2 % hinzufügen\n"
        "sudo tc qdisc change dev eth0 root netem \\\n"
        "    rate 5mbit delay 20ms loss 2%\n\n"
        "# Zurücksetzen\n"
        "sudo tc qdisc del dev eth0 root"
    )
    story.append(Paragraph(tc_code.replace("\n","<br/>").replace(" ","&nbsp;"),
                            S["code"]))

    story.append(Paragraph("6.2  Methode 2: Software-Traffic-Injektor", S["h2"]))
    story.append(Paragraph(
        "Ein Python-Skript sendet UDP-Dummy-Pakete schrittweise auf das Netzwerk "
        "und belastet so die gemeinsame Bandbreite. Vorteil: läuft ohne Root-Rechte "
        "und lässt sich in den Testrahmen integrieren:", S["body"]))

    inj_code = (
        "def flood(target_ip, port, mbits, duration_s):\n"
        "    sock = socket.socket(AF_INET, SOCK_DGRAM)\n"
        "    payload = b'x' * 1400           # ~MTU\n"
        "    delay = 1400 / (mbits * 1e6 / 8)\n"
        "    deadline = time.time() + duration_s\n"
        "    while time.time() < deadline:\n"
        "        sock.sendto(payload, (target_ip, port))\n"
        "        time.sleep(delay)\n\n"
        "# Stufenweise Last: 20 % → 50 % → 80 % → Erholung\n"
        "for mbits in [2, 5, 8, 0]:   # 0 = Erholung\n"
        "    flood('192.168.1.x', 5555, mbits, 30)"
    )
    story.append(Paragraph(inj_code.replace("\n","<br/>").replace(" ","&nbsp;"),
                            S["code"]))

    story.append(Paragraph("6.3  Testszenarien", S["h2"]))
    test_data = [
        ["Szenario", "Methode", "Erwartetes Verhalten", "Erfolgskriterium"],
        ["BW-Rampe 0→100 %","Injektor stufenweise",
         "P3 pausiert @60%, P2 drosselt @75%, nur P1 @90%",
         "Kein P1-Datenverlust; korrekte Zustandsübergänge"],
        ["Plötzlicher Vollausfall","tc netem rate 0.1mbit",
         "Sofortige Emergency-Aktivierung",
         "P1 weiter aktiv innerhalb <200 ms"],
        ["Kurzer Burst (3 s)","Injektor 3 s @95%",
         "Triage aktiv, danach Restore",
         "P2/P3 Backlog korrekt nachgesendet"],
        ["CPU-Last-Engpass","stress-ng --cpu 4",
         "CPU-Monitor löst Drosselung aus",
         "LSL-Timestamps bleiben konsistent"],
        ["Store-and-Forward-Prüfung","tc + Puffer-Inspektion",
         "Gepufferte Samples mit orig. Timestamps ankommen",
         "Re-Sync-Fehler < 5 ms"],
    ]
    tt = Table(test_data, colWidths=[3.2*cm, 3.0*cm, 4.8*cm, 4.3*cm])
    tt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), CORAL),
        ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GRAY_LIGHT, WHITE]),
        ("BOX",        (0,0),(-1,-1),0.5, GRAY_MID),
        ("INNERGRID",  (0,0),(-1,-1),0.3, GRAY_MID),
        ("VALIGN",     (0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING", (0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(tt)

    # ── 7 Offene Fragen ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("7  Offene Fragen und Diskussionspunkte", S["h1"]))
    story.append(section_rule())

    open_qs = [
        ("Rückkanal-Wahl",
         "Welche der drei Optionen (LSL Control, REST, MQTT) ist für die "
         "bestehende Infrastruktur am besten geeignet? "
         "Gibt es bereits einen HTTP-Server auf den Sensorknoten?"),
        ("BLE-Geräte-Firmware",
         "Welche der eingesetzten BLE-Sensoren erlauben eine SDK-seitige "
         "Ratenanpassung? Für Geräte ohne SDK muss Sub-Sampling auf "
         "Empfängerseite als Fallback akzeptiert werden."),
        ("Triage-Schwellenwerte",
         "Die vorgeschlagenen Schwellen (60 / 75 / 90 %) sind Ausgangspunkte. "
         "Sie müssen durch Messungen im M4P-Lab kalibriert werden – "
         "welche Bandbreite steht real zur Verfügung?"),
        ("Store-and-Forward-Umfang",
         "Soll der Puffer nur für Analyse-Daten dienen, oder auch für "
         "Promotions-Datensätze (vollständige Sitzungsaufzeichnung)? "
         "Letzteres erfordert erheblich mehr Disk-Kapazität."),
        ("5G-Integration",
         "Der Zwischenbericht sieht 5G als nächsten Schritt vor. "
         "Wie ändert sich die Triage-Logik, wenn 5G als Primärkanal "
         "und Wi-Fi als Fallback genutzt wird?"),
        ("Promotionsvorhaben",
         "Welche Aspekte des Ressourcenmanagements sollen Teil der Dissertation "
         "werden? Insbesondere: formale Bewertungsmetriken, adaptive Algorithmen "
         "oder empirische Evaluation der Triage-Entscheidungen?"),
    ]
    for title, body in open_qs:
        story.append(KeepTogether([
            Paragraph(f"<b>{title}</b>", S["h2"]),
            Paragraph(body, S["body"]),
        ]))

    # ── 8 Nächste Schritte ────────────────────────────────────────────────────
    story.append(Paragraph("8  Vorgeschlagene nächste Schritte", S["h1"]))
    story.append(section_rule())

    steps = [
        ("Kurzfristig (1–2 Monate)",  BLUE_MID, [
            "Prioritäts-Tags in bestehende LSL-Streams eintragen",
            "Einfachen Bandbreiten-Monitor (psutil) in DataHub integrieren",
            "Rückkanal Option A (LSL Control Stream) prototypisch umsetzen",
            "tc netem auf Testrechner einrichten und erste Schwellenwerte messen",
        ]),
        ("Mittelfristig (3–5 Monate)", TEAL, [
            "Vollständigen Triage-Zustandsautomaten implementieren",
            "Store-and-Forward-Buffer für Kamera und Temperatur",
            "Testszenarien aus Abschnitt 6.3 systematisch durchführen",
            "Ergebnisse in bestehenden Demonstrator integrieren (AP6)",
        ]),
        ("Langfristig (6+ Monate)",    AMBER, [
            "5G als Übertragungskanal evaluieren (AP5)",
            "Adaptives Ressourcenmanagement mit ML-basierten Schwellen",
            "Publikation der Triage-Ergebnisse (IEEE Transactions o.ä.)",
            "Generalisierung auf weitere Anwendungsfelder (Medizin, VR/AR)",
        ]),
    ]

    for phase, col, items in steps:
        story.append(ColorBox(phase, col, WHITE, height=22))
        story.append(Spacer(1, 0.15*cm))
        for item in items:
            story.append(Paragraph(f"• {item}", S["bullet"]))
        story.append(Spacer(1, 0.2*cm))

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_MID))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "Dieses Konzeptpapier dient als Diskussionsgrundlage für das ResCom-Projektteam "
        "(Embedded Robotics Lab, htw saar). Alle Schwellenwerte und Architekturentscheidungen "
        "sind vorläufig und bedürfen der Kalibrierung durch Messungen im M4P-Lab.",
        S["caption"]))

    doc.build(story)
    print("PDF written to", out)

build()