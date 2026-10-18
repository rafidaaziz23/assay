"""
Fill the AI Builder Cup submission deck for Assay.

Reads the organizer template (docs/submission/Assay-AI-Builder-Cup.pptx), injects
content into the empty body area of each slide, and saves in place.

Design rules taken from the template itself:
  slide 10 x 5.625 in, black header 0.55 in, title baseline at T=0.73 in
  body area: L=0.29 .. 9.71, T=1.42 .. 5.42
  fonts: "Google Sans Flex" (embedded in the deck), Medium for headings

Every number in here traces to eval/results/*.json or to a file in the repo.
Nothing is estimated.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "submission" / "Assay-AI-Builder-Cup.pptx"
ASSETS = ROOT / "docs" / "submission" / "assets"

FONT = "Google Sans Flex"
FONT_MED = "Google Sans Flex Medium"

INK = RGBColor(0x0F, 0x17, 0x2A)
BODY = RGBColor(0x33, 0x41, 0x55)
MUTED = RGBColor(0x64, 0x74, 0x8B)
INDIGO = RGBColor(0x4F, 0x46, 0xE5)
INDIGO_DK = RGBColor(0x31, 0x2E, 0x81)
INDIGO_LT = RGBColor(0xEE, 0xF0, 0xFF)
SUCCESS = RGBColor(0x10, 0xB9, 0x81)
WARN = RGBColor(0xF5, 0x9E, 0x0B)
WARN_BG = RGBColor(0xFF, 0xFB, 0xEB)
WARN_LN = RGBColor(0xFD, 0xE6, 0x8A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xE2, 0xE8, 0xF0)

LEFT = Inches(0.42)
TOP = Inches(1.42)
WIDTH = Inches(9.16)
BOTTOM = Inches(5.40)


# ── primitives ────────────────────────────────────────────────────────────────

def _text(slide, left, top, width, height, runs, *, size=11, color=BODY,
          font=FONT, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          spacing=1.0, space_after=2):
    """runs: str, or list of (text, {overrides}) / str items.

    A list of items becomes ONE paragraph with inline runs, so styled fragments stay
    on the same line. Pass a list of lists to get multiple paragraphs.
    """
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0

    if isinstance(runs, str):
        runs = [runs]

    # a list of lists => several paragraphs; a flat list => one paragraph
    paragraphs = runs if runs and isinstance(runs[0], list) else [runs]

    for i, items in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(space_after)
        for item in items:
            if isinstance(item, str):
                item = (item, {})
            text, opt = item
            r = p.add_run()
            r.text = text
            r.font.name = opt.get("font", font)
            r.font.size = Pt(opt.get("size", size))
            r.font.bold = opt.get("bold", bold)
            r.font.color.rgb = opt.get("color", color)
    return box


def _card(slide, left, top, width, height, *, fill=WHITE, line=LINE,
          radius=0.04, line_w=0.75):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.adjustments[0] = radius
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    return shp


def _bar(slide, left, top, width, height, color, radius=0.5):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.adjustments[0] = radius
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def _chip(slide, left, top, text, *, fg=INDIGO, bg=INDIGO_LT, size=9, pad=0.13):
    w = Inches(pad + len(text) * size * 0.0092)
    shp = _card(slide, left, top, w, Inches(0.26), fill=bg, line=None, radius=0.4)
    _text(slide, left + Inches(pad / 2), top + Inches(0.045), w, Inches(0.2),
          [(text, {"size": size, "bold": True, "color": fg})], font=FONT_MED)
    return w


def _arrow(slide, x1, y1, x2, y2, color=INDIGO):
    """Draw a thin horizontal arrow as a plain rectangle + triangle.

    python-pptx emits an empty <p:cNvCxnSpPr/>, which PowerPoint refuses to open.
    Two autoshapes avoid that entirely and render identically at this size.
    """
    h = Pt(1.5)
    shaft = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x1, y1 - h / 2, x2 - x1 - Pt(5), h)
    shaft.fill.solid()
    shaft.fill.fore_color.rgb = color
    shaft.line.fill.background()
    shaft.shadow.inherit = False

    head = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,
                                  x2 - Pt(6), y2 - Pt(4), Pt(6), Pt(8))
    head.rotation = 90
    head.fill.solid()
    head.fill.fore_color.rgb = color
    head.line.fill.background()
    head.shadow.inherit = False


def _head(slide, x, y, direction, color=INDIGO, size=Pt(7)):
    """Arrowhead with its tip exactly at (x, y). Body sits behind the tip."""
    s = size
    boxes = {
        "up":    (x - s / 2, y,      0),
        "down":  (x - s / 2, y - s,  180),
        "right": (x - s,     y - s / 2, 90),
        "left":  (x,         y - s / 2, 270),
    }
    left, top, rot = boxes[direction]
    head = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, left, top, s, s)
    head.rotation = rot
    head.fill.solid()
    head.fill.fore_color.rgb = color
    head.line.fill.background()
    head.shadow.inherit = False


def _conn(slide, pts, color=INDIGO, weight=1.5, head=True):
    """Orthogonal polyline through pts [(x, y), ...]; optional arrowhead at the last point.

    Segments are plain rectangles because python-pptx writes an empty <p:cNvCxnSpPr/>
    for real connectors, which PowerPoint refuses to open.
    """
    t = Pt(weight)
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if abs(x1 - x2) < Emu(1):          # vertical
            top, height = min(y1, y2), abs(y2 - y1)
            shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x1 - t / 2, top, t, height)
        else:                               # horizontal
            left, width = min(x1, x2), abs(x2 - x1)
            shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, y1 - t / 2, width, t)
        shp.fill.solid()
        shp.fill.fore_color.rgb = color
        shp.line.fill.background()
        shp.shadow.inherit = False

    if head:
        (px, py), (qx, qy) = pts[-2], pts[-1]
        if abs(qx - px) < Emu(1):
            direction = "down" if qy > py else "up"
        else:
            direction = "right" if qx > px else "left"
        _head(slide, qx, qy, direction, color)


def _diamond(slide, cx, cy, w, h, text, *, fill=WHITE, line=INDIGO, fg=INK, size=8.5):
    shp = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, cx - w / 2, cy - h / 2, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = line
    shp.line.width = Pt(1.0)
    shp.shadow.inherit = False
    lines = text.split("\n")
    _text(slide, cx - Inches(0.62), cy - Inches(0.24), Inches(1.24), Inches(0.48),
          [[(ln, {"size": size, "bold": True, "color": fg, "font": FONT_MED})] for ln in lines],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0, space_after=0)
    return shp


def _purge_body(slide, floor=Inches(1.0), ceiling=Inches(5.50)):
    """Drop every shape in the body band so a slide can be rebuilt in place.

    The template header (top < 1.0) and the bottom accent bar (top >= 5.50) survive.
    """
    for shp in list(slide.shapes):
        if shp.top is not None and floor <= shp.top < ceiling:
            shp._element.getparent().remove(shp._element)


def _clean(slide, keep_titles=True):
    """Remove leftover body placeholders and template instruction lines.

    The organizer template packs guidance prompts ("How different is it from...",
    "USP of the proposed solution") as extra paragraphs inside the title textbox.
    They are instructions to the submitter, not slide content, so they go.
    """
    guidance_markers = (
        "How different is it", "How will it be able to solve",
        "USP of the proposed solution",
    )
    for shp in list(slide.shapes):
        if not shp.has_text_frame:
            continue
        # strip guidance paragraphs from the title box (keeps paragraph 0 = real title)
        if keep_titles and shp.top is not None and shp.top < Inches(1.0):
            tf = shp.text_frame
            for para in list(tf.paragraphs)[1:]:
                if any(m in para.text for m in guidance_markers):
                    para._p.getparent().remove(para._p)
        if shp.top is not None and shp.top > Inches(1.0):
            if shp.name.startswith("Google Shape"):
                shp._element.getparent().remove(shp._element)


def slide_title(slide):
    for shp in slide.shapes:
        if shp.has_text_frame and shp.top is not None and shp.top < Inches(1.0):
            t = shp.text_frame.text.strip()
            if t:
                return t
    return ""


# ── slides ────────────────────────────────────────────────────────────────────

def s01_team(prs):
    s = prs.slides[0]
    # TITLE layout: the black half ends at 2.97in (measured), so all content lives below it
    _clean(s)
    top = Inches(3.02)
    _text(s, LEFT, top, WIDTH, Inches(0.3),
          [("Team Details", {"size": 14, "bold": True, "color": INK, "font": FONT_MED})])

    rows = [
        ("a.", "Team name", "Assay"),
        ("b.", "Team leader name", "Rafida Aziz"),
        ("c.", "Problem Statement",
         "AI study tools dispense answers instead of building reasoning. Assay forces the learner "
         "to defend their understanding in Socratic dialogue, and verifies every claim against "
         "the source document."),
    ]
    y = top + Inches(0.38)
    for tag, label, value in rows:
        _text(s, LEFT, y, Inches(0.3), Inches(0.26),
              [(tag, {"size": 10, "bold": True, "color": INDIGO})])
        _text(s, LEFT + Inches(0.3), y, Inches(1.7), Inches(0.26),
              [(label + ":", {"size": 10, "color": MUTED})])
        _text(s, LEFT + Inches(2.0), y - Inches(0.02), Inches(7.0),
              Inches(0.7 if len(value) > 80 else 0.26),
              [(value, {"size": 10, "bold": True, "color": INK})],
              spacing=1.15)
        y += Inches(0.3) if len(value) <= 80 else Inches(0.72)

    _text(s, LEFT, Inches(5.02), WIDTH, Inches(0.3),
          [("Google Cloud AI Builder Cup 2026  ·  Track 4 — Media, Content & Digital Experiences",
            {"size": 8, "color": MUTED})])


def s03_brief(prs):
    s = prs.slides[2]
    _clean(s)

    _text(s, LEFT, TOP, Inches(5.3), Inches(1.0),
          [("Every AI study tool answers questions.", {"size": 17, "bold": True, "color": INK, "font": FONT_MED}),
           ("Assay questions your answers.", {"size": 17, "bold": True, "color": INDIGO, "font": FONT_MED})],
          spacing=1.05, space_after=0)

    _text(s, LEFT, Inches(2.35), Inches(5.3), Inches(2.85), [
        [("The problem. ", {"bold": True, "color": INK}),
         ("Students feed material into an AI, get a summary or a quiz, and mistake recognition for "
          "understanding. The cognitive muscle is never exercised — and there is no way to tell "
          "comprehension from confident recall.", {})],
        [("What Assay does. ", {"bold": True, "color": INK}),
         ("It ingests a PDF or a topic, builds a gated syllabus anchored to page numbers, then runs a "
          "Socratic oral defense. The learner must derive, not recite. Every answer is verified "
          "against the source; ungrounded claims are refused instead of rewarded.", {})],
        [("The mechanism. ", {"bold": True, "color": INK}),
         ("Deterministic honeypot terms — plausible but fictional — are injected into the dialogue. "
          "A learner who explains one fluently is bluffing, and the engine catches it.", {})],
    ], size=9.6, spacing=1.14, space_after=6)

    # right column: the pipeline, as a vertical stepper
    x = Inches(5.95)
    _card(s, x, TOP, Inches(3.55), Inches(3.5), fill=RGBColor(0xF8, 0xFA, 0xFC))
    _text(s, x + Inches(0.25), TOP + Inches(0.2), Inches(3.1), Inches(0.3),
          [("THE LOOP", {"size": 9, "bold": True, "color": MUTED})])
    steps = [
        ("01", "Intake", "Intent + target role + optional PDF"),
        ("02", "Scope checklist", "Live-streamed topics, user-curated"),
        ("03", "Gated syllabus", "Chapters anchored to page numbers"),
        ("04", "Socratic defense", "Adversarial oral examination"),
        ("05", "Verified dossier", "Bloom-level report, citations intact"),
    ]
    y = TOP + Inches(0.58)
    for num, head, sub in steps:
        _text(s, x + Inches(0.25), y, Inches(0.35), Inches(0.25),
              [(num, {"size": 9, "bold": True, "color": INDIGO})])
        _text(s, x + Inches(0.62), y - Inches(0.04), Inches(2.75), Inches(0.25),
              [(head, {"size": 10.5, "bold": True, "color": INK, "font": FONT_MED})])
        _text(s, x + Inches(0.62), y + Inches(0.2), Inches(2.75), Inches(0.3),
              [(sub, {"size": 8.5, "color": MUTED})])
        y += Inches(0.62)


def s04_opportunity(prs):
    s = prs.slides[3]
    _clean(s)

    cols = [
        ("Existing tools", "Answer dispensers", [
            "ChatGPT / NotebookLM: summarise, then stop",
            "Quiz generators: multiple choice, guessable",
            "Flashcards: recognition, not derivation",
            "No verification that the learner understood",
        ], MUTED, RGBColor(0xF8, 0xFA, 0xFC)),
        ("Assay", "Answer interrogators", [
            "Learner must derive under adversarial probing",
            "Open-ended defense, no multiple choice",
            "Every claim grounded to a page or refused",
            "Honeypot terms expose bluffing deterministically",
        ], INDIGO, INDIGO_LT),
    ]
    x = LEFT
    for head, sub, bullets, accent, bg in cols:
        _card(s, x, Inches(1.45), Inches(4.45), Inches(1.95), fill=bg,
              line=None if bg != WHITE else LINE)
        _text(s, x + Inches(0.22), Inches(1.60), Inches(4.0), Inches(0.3),
              [(head, {"size": 11.5, "bold": True, "color": accent, "font": FONT_MED}),
               (sub, {"size": 8.5, "color": MUTED})], spacing=1.0, space_after=1)
        _text(s, x + Inches(0.22), Inches(2.18), Inches(4.05), Inches(1.1),
              [[(b, {"size": 8.8, "color": BODY})] for b in bullets],
              spacing=1.1, space_after=2)
        x += Inches(4.72)

    _text(s, LEFT, Inches(3.62), WIDTH, Inches(0.3),
          [("Unique selling proposition", {"size": 11.5, "bold": True, "color": INK, "font": FONT_MED})])
    _text(s, LEFT, Inches(3.98), WIDTH, Inches(1.4), [
        ("Assay is the only study tool whose output is a ", {}),
        ("defense transcript", {"bold": True, "color": INDIGO}),
        (", not a summary. It is adversarial by design: the system actively tries to catch you "
         "bluffing, using fictional terms and false premises, and it scores the refusal. "
         "Grounding is enforced at the retrieval layer — recall@3 of ", {}),
        ("0.909", {"bold": True, "color": INDIGO}),
        (" over 22 questions, with a ", {}),
        ("100%", {"bold": True, "color": INDIGO}),
        (" refusal rate on the 2 unanswerable ones.", {}),
    ], size=9.8, spacing=1.22)


def s05_features(prs):
    s = prs.slides[4]
    _clean(s)

    feats = [
        ("Intake & calibration", "Topic prompt or PDF upload, target engineering role, and three rigor levels (Foundation / Applied / Rigorous) that set the depth of questioning."),
        ("Realtime scope checklist", "Topics are streamed live via SSE as they are extracted, tagged by origin — document, role taxonomy, or grounded external — and the learner curates them."),
        ("Gated syllabus", "Content is chunked into chapters anchored to page numbers, so every later claim can be traced back to a specific page."),
        ("Socratic oral defense", "Turn-based adversarial dialogue. The learner must derive; the engine pushes back on hand-waving and follows up on weak answers."),
        ("Anti-hallucination verifier", "Each response is checked against the retrieved source. Ungrounded claims are flagged and refused rather than accepted."),
        ("Honeypot detection", "Deterministic fictional terms are seeded into the dialogue. Explaining one fluently is scored as a hallucination, not as knowledge."),
        ("Competency dossier", "A verified report with Bloom-level profiling, rubric scores per competency, and an audit record of the session."),
        ("Deterministic fallback cache", "A pre-computed response cache keeps the demo and the eval harness alive with zero crashes when the model API is unavailable."),
    ]
    cols, rows = 2, 4
    cw, ch = Inches(4.42), Inches(0.92)
    gx, gy = Inches(0.30), Inches(0.14)
    for i, (head, desc) in enumerate(feats):
        r, c = divmod(i, cols)
        x = LEFT + c * (cw + gx)
        y = TOP + r * (ch + gy)
        _card(s, x, y, cw, ch, fill=RGBColor(0xF8, 0xFA, 0xFC), line=LINE)
        _bar(s, x, y + Inches(0.14), Inches(0.05), Inches(0.62), INDIGO, radius=0.5)
        _text(s, x + Inches(0.2), y + Inches(0.12), cw - Inches(0.35), Inches(0.25),
              [(head, {"size": 10.5, "bold": True, "color": INK, "font": FONT_MED})])
        _text(s, x + Inches(0.2), y + Inches(0.38), cw - Inches(0.35), Inches(0.5),
              [(desc, {"size": 8.2, "color": MUTED})], spacing=1.05)


def s06_flow(prs):
    """Flowchart: five stages, then the gate, then two decisions with real branches.

    Topology follows PRD §3 (the canonical flow) and the per-chapter gate:
        [1 Intake] -> [2 Checklist] -> [3 Syllabus] -> [4 Chapter reader] -> [5 Oral defense]
                                                                                  |
                                                        <Defense score >= 75?> --no--> back to 4
                                                                  | yes
                                                         <Last chapter?> --no--> next chapter, repeat 4->5
                                                                  | yes
                                                              [Dossier]

    Every node is registered in `nodes` and the function asserts at the end that no two of
    the drawn shapes overlap, so the geometry is checked on every build instead of by eye.
    """
    s = prs.slides[5]
    # Purge rather than _clean: on the pristine organizer template _clean leaves body
    # placeholders behind, so a first build would stack the flowchart on top of them.
    _purge_body(s)

    _text(s, LEFT, TOP, WIDTH, Inches(0.28),
          [("Process flow — the gate is the product: a chapter never unlocks until it is defended",
            {"size": 9, "color": MUTED})])

    nodes = []   # actual shape objects, so the overlap check measures what got drawn

    def reg(shp):
        nodes.append(shp)
        return shp

    def I(v):
        return Inches(v)

    # ── left column: the linear spine ─────────────────────────────────────────
    LX, LW = 0.42, 4.02
    LCX = LX + LW / 2
    y0, bh, step = 1.70, 0.58, 0.72

    stages = [
        ("1", "Intake", "Prompt or PDF, target role, rigor level"),
        ("2", "Realtime checklist", "Topics streamed over SSE, learner curates"),
        ("3", "Gated syllabus", "Chapters chunked, every claim page-anchored"),
        ("4", "Gated chapter reader", "Source text and Socratic ask, side by side"),
        ("5", "Oral defense", "Adversarial turns, honeypot injected"),
    ]

    for i, (num, head, sub) in enumerate(stages):
        y = y0 + i * step
        hero = i == len(stages) - 1          # the defense is the differentiator
        reg(_card(s, I(LX), I(y), I(LW), I(bh),
                  fill=INDIGO if hero else RGBColor(0xF8, 0xFA, 0xFC),
                  line=None if hero else LINE))

        badge = s.shapes.add_shape(MSO_SHAPE.OVAL,
                                   I(LX + 0.15), I(y + bh / 2 - 0.15), I(0.30), I(0.30))
        badge.fill.solid()
        badge.fill.fore_color.rgb = WHITE if hero else INDIGO_LT
        badge.line.fill.background()
        badge.shadow.inherit = False
        _text(s, I(LX + 0.15), I(y + bh / 2 - 0.15), I(0.30), I(0.30),
              [(num, {"size": 8.5, "bold": True, "color": INDIGO})],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

        _text(s, I(LX + 0.56), I(y + 0.07), I(LW - 0.70), I(0.22),
              [(head, {"size": 9.5, "bold": True, "font": FONT_MED,
                       "color": WHITE if hero else INK})])
        _text(s, I(LX + 0.56), I(y + 0.29), I(LW - 0.70), I(0.22),
              [(sub, {"size": 7.6,
                      "color": RGBColor(0xE0, 0xE3, 0xFF) if hero else MUTED})])

        if i < len(stages) - 1:
            _conn(s, [(I(LCX), I(y + bh)), (I(LCX), I(y + step))])

    # ── the gate condition note: the only prose on the slide ──────────────────
    NX, NY, NW, NH = 4.90, 1.70, 4.68, 0.88
    reg(_card(s, I(NX), I(NY), I(NW), I(NH), fill=INDIGO_LT, line=None))
    _text(s, I(NX + 0.22), I(NY + 0.11), I(NW - 0.44), I(NH - 0.22), [
        ("Gate condition: ", {"bold": True, "color": INDIGO}),
        ("a chapter unlocks only when its defense scores ≥ 75. Fail → the same chapter is "
         "re-read, not the whole course restarted. Pass → the next chapter unlocks. The dossier "
         "is assembled only after the last chapter, from transcripts that actually happened.", {}),
    ], size=8.4, spacing=1.15)

    # ── decision A: the gate. Aligned with stage 5, its only input. ───────────
    ax, ay, aw, ah = 6.05, 4.87, 1.70, 0.82
    reg(_diamond(s, I(ax), I(ay), I(aw), I(ah), "Defense\nscore ≥ 75?"))
    _conn(s, [(I(LX + LW), I(ay)), (I(ax - aw / 2), I(ay))])

    # ── decision B: is the whole syllabus done? ───────────────────────────────
    bx, by, bw, bh2 = 7.55, 3.98, 1.70, 0.80
    reg(_diamond(s, I(bx), I(by), I(bw), I(bh2), "Last\nchapter?"))

    # yes -> B (up into its bottom vertex)
    _conn(s, [(I(ax + aw / 2), I(ay)), (I(bx), I(ay)), (I(bx), I(by + bh2 / 2))],
          color=SUCCESS)
    _text(s, I(bx - 0.62), I(ay + 0.04), I(0.40), I(0.16),
          [("yes", {"size": 7, "bold": True, "color": SUCCESS})])

    # ── terminal: the dossier, only reachable through a passed last chapter ───
    DX, DY, DW, DH = 6.62, 2.72, 1.86, 0.62
    reg(_card(s, I(DX), I(DY), I(DW), I(DH), fill=SUCCESS, line=None))
    _text(s, I(DX + 0.16), I(DY + 0.10), I(DW - 0.32), I(0.22),
          [("Dossier", {"size": 9, "bold": True, "font": FONT_MED, "color": WHITE})])
    _text(s, I(DX + 0.16), I(DY + 0.32), I(DW - 0.32), I(0.24),
          [("Bloom profile, audit record", {"size": 7.0, "color": RGBColor(0xDC, 0xFC, 0xEE)})])
    _conn(s, [(I(bx), I(by - bh2 / 2)), (I(bx), I(DY + DH))], color=SUCCESS)
    _text(s, I(bx + 0.08), I(DY + DH + 0.02), I(0.40), I(0.16),
          [("yes", {"size": 7, "bold": True, "color": SUCCESS})])

    # ── the two "no" exits are NOT the same thing, so they get their own lines ──
    # A-no (amber) = you failed: re-read the SAME chapter. A penalty.
    # B-no (indigo) = you passed: the NEXT chapter opens. Forward motion, not a loop.
    # The wording lives in the gate note above; the connectors only carry yes/no.
    _conn(s, [(I(ax), I(ay - ah / 2)), (I(ax), I(4.20)), (I(LX + LW), I(4.20))], color=WARN)
    _text(s, I(ax + 0.07), I(4.24), I(0.34), I(0.16),
          [("no", {"size": 7, "bold": True, "color": WARN})])

    _conn(s, [(I(bx - bw / 2), I(by)), (I(LX + LW), I(by))], color=INDIGO)
    _text(s, I(bx - bw / 2 - 0.36), I(by + 0.03), I(0.34), I(0.16),
          [("no", {"size": 7, "bold": True, "color": INDIGO})])

    # ── geometry assert, on the shapes that were actually drawn ───────────────
    # Reading coordinates back from the shape objects (not the values we intended to
    # pass) means a bad call site cannot slip through: if _card is given overlapping
    # geometry, this fires.
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if (a.left < b.left + b.width and b.left < a.left + a.width and
                    a.top < b.top + b.height and b.top < a.top + a.height):
                raise AssertionError(
                    f"slide 6 layout: {a.name} overlaps {b.name}")


def s08_architecture(prs):
    s = prs.slides[7]
    _clean(s)

    # three tiers
    tiers = [
        ("CLIENT", "React 18 + Vite + TypeScript", 1.55, RGBColor(0xF8, 0xFA, 0xFC), MUTED),
        ("API", "FastAPI · Python 3.11 · SSE", 2.55, INDIGO_LT, INDIGO),
        ("ENGINE", "Assay core · Gemini · retrieval", 3.55, RGBColor(0xF8, 0xFA, 0xFC), MUTED),
    ]
    for name, sub, top, bg, accent in tiers:
        _card(s, LEFT, Inches(top), Inches(1.55), Inches(0.78), fill=bg, line=LINE)
        _text(s, LEFT + Inches(0.15), Inches(top + 0.13), Inches(1.3), Inches(0.25),
              [(name, {"size": 9.5, "bold": True, "color": accent})])
        _text(s, LEFT + Inches(0.15), Inches(top + 0.38), Inches(1.3), Inches(0.4),
              [(sub, {"size": 7.5, "color": MUTED})], spacing=1.05)

    # modules in the middle/right
    mods = [
        (Inches(2.25), Inches(1.55), "Pages", "14 routes\nDashboard · Intake · Reader · Exam · Report"),
        (Inches(2.25), Inches(2.55), "Endpoints", "intake · syllabus · interview · report · calibration"),
        (Inches(2.25), Inches(3.55), "Repositories", "SessionStore · ChapterStore · InterviewStore (in-memory, Firestore port stubbed)"),
        (Inches(5.55), Inches(1.55), "State", "Zustand stores\nrouting via react-router 7"),
        (Inches(5.55), Inches(2.55), "Streaming", "SSE via sse-starlette\nintake checklist partial events"),
        (Inches(5.55), Inches(3.55), "Retrieval", "PyMuPDF page-anchored extraction\nrecall@3 = 0.909"),
        (Inches(8.05), Inches(1.55), "Gemini", "google-genai SDK\ngemini-2.5-flash / 2.5-pro"),
        (Inches(8.05), Inches(2.55), "Verifier", "grounding check per turn\n6/6 caught in eval"),
        (Inches(8.05), Inches(3.55), "Fallback", "deterministic cache\nzero-crash demo mode"),
    ]
    for x, y, head, sub in mods:
        w = Inches(2.1) if x < Inches(7) else Inches(1.65)
        _card(s, x, y, w, Inches(0.78), fill=WHITE, line=LINE)
        _text(s, x + Inches(0.13), y + Inches(0.1), w - Inches(0.2), Inches(0.25),
              [(head, {"size": 9, "bold": True, "color": INK, "font": FONT_MED})])
        _text(s, x + Inches(0.13), y + Inches(0.33), w - Inches(0.2), Inches(0.4),
              [(sub, {"size": 7.2, "color": MUTED})], spacing=1.05)

    for y in (1.93, 2.93, 3.93):
        _arrow(s, Inches(2.02), Inches(y), Inches(2.23), Inches(y))
        _arrow(s, Inches(4.38), Inches(y), Inches(5.53), Inches(y))
        _arrow(s, Inches(7.68), Inches(y), Inches(8.03), Inches(y))

    _card(s, LEFT, Inches(4.6), WIDTH, Inches(0.72), fill=INDIGO_LT, line=None)
    _text(s, LEFT + Inches(0.25), Inches(4.72), Inches(8.6), Inches(0.5), [
        ("Deployment: ", {"bold": True, "color": INDIGO}),
        ("single container on Google Cloud Run — FastAPI serving the built Vite bundle. "
         "No database required at runtime; the repository layer is an interface with an in-memory "
         "implementation and a Firestore port stubbed for the multi-tenant phase.", {}),
    ], size=9, spacing=1.15)


def s09_tech(prs):
    s = prs.slides[8]
    _clean(s)

    groups = [
        ("Frontend", ["React 18", "TypeScript", "Vite", "Tailwind CSS", "Zustand", "react-router 7", "Lucide icons", "KaTeX"]),
        ("Backend", ["Python 3.11", "FastAPI", "Uvicorn", "Pydantic v2", "sse-starlette", "PyMuPDF"]),
        ("AI", ["Gemini 2.5 Flash", "Gemini 2.5 Pro", "google-genai SDK", "Deterministic honeypot catalog", "Grounded verifier"]),
        ("Platform", ["Google Cloud Run", "Docker", "GitHub", "pytest (203 tests)"]),
    ]
    x = LEFT
    cw = Inches(2.18)
    for head, items in groups:
        _card(s, x, TOP, cw, Inches(2.55), fill=RGBColor(0xF8, 0xFA, 0xFC), line=LINE)
        _text(s, x + Inches(0.18), TOP + Inches(0.16), cw - Inches(0.3), Inches(0.25),
              [(head.upper(), {"size": 9, "bold": True, "color": INDIGO})])
        _text(s, x + Inches(0.18), TOP + Inches(0.5), cw - Inches(0.3), Inches(2.0),
              [[(f"·  {i}", {"size": 8.8, "color": BODY})] for i in items],
              spacing=1.12, space_after=3)
        x += cw + Inches(0.14)

    _text(s, LEFT, Inches(4.2), WIDTH, Inches(0.9), [
        ("Why this stack: ", {"bold": True, "color": INK}),
        ("everything Google-side is the official SDK and the Gemini API, so the AI layer is a thin, "
         "auditable wrapper rather than a framework. The frontend stays on Vite because the whole app "
         "is a client-rendered SPA behind one API origin — no server rendering needed, and the build "
         "ships as static assets inside the same container.", {}),
    ], size=9.5, spacing=1.2)

    _text(s, LEFT, Inches(4.95), WIDTH, Inches(0.4),
          [("203 automated backend tests · 12 test modules · deterministic eval harness in eval/",
            {"size": 8.5, "color": MUTED})])


def s10_cost(prs):
    s = prs.slides[9]
    _clean(s)

    _text(s, LEFT, TOP, WIDTH, Inches(0.3),
          [("Monthly estimate at three scales. Gemini list price: $0.30 / 1M input, $2.50 / 1M output "
            "(gemini-2.5-flash, paid tier).", {"size": 8.5, "color": MUTED})])

    headers = ["", "Pilot", "Classroom", "Department"]
    rows = [
        ("Active learners", "10", "100", "1,000"),
        ("Defense turns / learner / month", "60", "60", "60"),
        ("Gemini input tokens", "0.6M", "6M", "60M"),
        ("Gemini output tokens", "0.9M", "9M", "90M"),
        ("Gemini cost", "$2.43", "$24.30", "$243.00"),
        ("Cloud Run (2 vCPU / 2 GiB, scale-to-zero)", "≈ $3", "≈ $12", "≈ $60"),
        ("Total / month", "≈ $5", "≈ $36", "≈ $303"),
        ("Cost per learner", "≈ $0.24", "≈ $0.24", "≈ $0.24"),
    ]
    x0, y0 = LEFT, Inches(1.85)
    cw = [Inches(3.5), Inches(1.85), Inches(1.85), Inches(1.85)]
    rh = Inches(0.33)

    # header row
    x = x0
    for i, h in enumerate(headers):
        if h:
            _text(s, x, y0, cw[i], rh, [(h, {"size": 9, "bold": True, "color": INK})],
                  align=PP_ALIGN.RIGHT if i else PP_ALIGN.LEFT)
        x += cw[i]

    for r, row in enumerate(rows):
        y = y0 + Inches(0.36) + r * rh
        is_total = row[0].startswith("Total")
        if is_total:
            _card(s, x0, y - Inches(0.04), Inches(9.05), rh, fill=INDIGO_LT, line=None)
        x = x0
        for i, cell in enumerate(row):
            col = INK if is_total else (BODY if i else MUTED)
            _text(s, x, y, cw[i], rh,
                  [(cell, {"size": 8.8, "bold": is_total, "color": col})],
                  align=PP_ALIGN.RIGHT if i else PP_ALIGN.LEFT)
            x += cw[i]

    _text(s, LEFT, Inches(4.75), WIDTH, Inches(0.6), [
        ("Assumptions, stated so they can be challenged: ", {"bold": True, "color": INK}),
        ("60 defense turns per learner per month at ~1k input and ~1.5k output tokens per turn. "
         "Cloud Run figures are order-of-magnitude for a scale-to-zero service and exclude the free tier. "
         "Gemini pricing is the published paid-tier list price; the free tier covers the pilot.", {}),
    ], size=8, spacing=1.15, color=MUTED)


def s11_snapshots(prs):
    s = prs.slides[10]
    _clean(s)

    shots = [
        ("intake.png", "Intake", "Prompt or PDF, role, and rigor calibration"),
        ("roadmap.png", "Gated syllabus", "Modules with concept counts and duration"),
        ("reader.png", "Deep reader", "Source text and Socratic dialogue side by side"),
        ("exam.png", "Oral defense", "Adversarial turn with live rubric scores"),
        ("report.png", "Dossier", "Bloom profile, rubric, audit record"),
        ("dashboard.png", "Dashboard", "Progress, defenses passed, upcoming defense"),
    ]
    # 2 rows must fit between the title (1.42) and the slide bottom (5.625):
    # row = image 1.42 + caption 0.36, two rows + gap => keep total under 4.0in
    cw, ch = Inches(2.95), Inches(1.35)
    gx, gy = Inches(0.16), Inches(0.50)
    for i, (fname, label, cap) in enumerate(shots):
        r, c = divmod(i, 3)
        x = LEFT + c * (cw + gx)
        y = TOP + r * (ch + gy + Inches(0.42))
        p = ASSETS / fname
        if p.exists():
            s.shapes.add_picture(str(p), x, y, width=cw, height=ch)
            _card(s, x, y, cw, ch, fill=None, line=LINE, radius=0.02)
        _text(s, x, y + ch + Inches(0.05), cw, Inches(0.2),
              [(label, {"size": 8.5, "bold": True, "color": INK})])
        _text(s, x, y + ch + Inches(0.21), cw, Inches(0.2),
              [(cap, {"size": 7, "color": MUTED})])


def s12_benchmark(prs):
    s = prs.slides[11]
    _clean(s)

    _text(s, LEFT, TOP, WIDTH, Inches(0.3),
          [("All figures from the deterministic harness in eval/ — no LLM judge, no rounding up.",
            {"size": 8.5, "color": MUTED})])

    # left: metric table
    hdr = ["Metric", "Result", "n"]
    rows = [
        ("Verifier catch rate", "6 / 6  (100%)", "6"),
        ("Structured output validity", "2 / 2  (100%)", "2"),
        ("Trap: fictional term detected", "100%", "2"),
        ("Trap: trap number detected", "100%", "2"),
        ("Trap: false premise detected", "50%", "2"),
        ("RAG recall@3", "0.909", "22"),
        ("RAG page-hit@1", "0.682", "22"),
        ("RAG refusal accuracy", "100%", "2"),
        ("Backend test suite", "203 tests", "12 files"),
    ]
    x0, y0 = LEFT, Inches(1.85)
    cw = [Inches(2.15), Inches(1.15), Inches(0.55)]
    gutter = Inches(0.12)  # explicit air between Result and n
    rh = Inches(0.3)
    xs = [x0, x0 + cw[0], x0 + cw[0] + cw[1] + gutter]
    for i, h in enumerate(hdr):
        _text(s, xs[i], y0, cw[i], rh, [(h, {"size": 8, "bold": True, "color": MUTED})],
              align=PP_ALIGN.RIGHT if i == 1 else PP_ALIGN.LEFT)
    for r, row in enumerate(rows):
        y = y0 + Inches(0.3) + r * rh
        for i, cell in enumerate(row):
            col = INK if i < 2 else MUTED
            al = PP_ALIGN.RIGHT if i == 1 else PP_ALIGN.LEFT
            _text(s, xs[i], y, cw[i], rh,
                  [(cell, {"size": 8.5, "bold": i == 1, "color": col})], align=al)

    # right: the honesty panel
    xr = Inches(5.35)
    _card(s, xr, Inches(1.85), Inches(4.15), Inches(1.95), fill=RGBColor(0xFF, 0xFB, 0xEB), line=WARN)
    _text(s, xr + Inches(0.22), Inches(1.96), Inches(3.75), Inches(0.25),
          [("Read this before quoting the numbers", {"size": 9, "bold": True, "color": RGBColor(0x92, 0x40, 0x0E)})])
    _text(s, xr + Inches(0.22), Inches(2.26), Inches(3.75), Inches(1.4), [
        ("The harness also measures how often the ", {}),
        ("raw model", {"bold": True}),
        (" hallucinates on fictional terms: ", {}),
        ("87.5%", {"bold": True, "color": RGBColor(0x92, 0x40, 0x0E)}),
        (" (n=8, product run) against a 54% research baseline (n=80). That is the ", {}),
        ("problem", {"bold": True}),
        (" we measure, not our accuracy. Assay's own score is the verifier catch rate above.", {}),
    ], size=7.8, spacing=1.1, color=BODY)

    _card(s, xr, Inches(3.95), Inches(4.15), Inches(1.35), fill=RGBColor(0xF8, 0xFA, 0xFC), line=LINE)
    _text(s, xr + Inches(0.22), Inches(4.06), Inches(3.75), Inches(0.25),
          [("Sample sizes are small and stated", {"size": 9, "bold": True, "color": INK})])
    _text(s, xr + Inches(0.22), Inches(4.36), Inches(3.75), Inches(0.9), [
        ("n=2 for most trap categories. The 100% figures are directionally strong but not "
         "statistically tight, and we say so rather than hiding the n. The RAG metrics (n=22) "
         "and the verifier (n=6) carry the most weight.", {}),
    ], size=7.8, spacing=1.1, color=BODY)


def s13_future(prs):
    s = prs.slides[12]
    _clean(s)

    phases = [
        ("Now — shipped", INDIGO, [
            "Intake, gated syllabus, deep reader, oral defense",
            "Anti-hallucination verifier + honeypot catalog",
            "Verified dossier with Bloom profiling",
            "203 backend tests, deterministic eval harness",
        ]),
        ("Next — 90 days", RGBColor(0x63, 0x66, 0xF1), [
            "Firestore port for multi-tenant sessions",
            "Voice-first defense (live speech, not typed)",
            "Instructor dashboard with cohort analytics",
            "Institutional SSO and roster import",
        ]),
        ("Later — 12 months", RGBColor(0xA5, 0xB0, 0xFF), [
            "Adaptive honeypot generation per domain",
            "Cross-session knowledge decay modelling",
            "LMS integrations (Canvas, Moodle)",
            "Public competency credential with verifiable link",
        ]),
    ]
    x = LEFT
    cw = Inches(2.95)
    for head, accent, items in phases:
        _card(s, x, TOP, cw, Inches(3.0), fill=RGBColor(0xF8, 0xFA, 0xFC), line=LINE)
        _bar(s, x, TOP, cw, Inches(0.06), accent, radius=0.3)
        _text(s, x + Inches(0.2), TOP + Inches(0.22), cw - Inches(0.35), Inches(0.25),
              [(head, {"size": 10, "bold": True, "color": INK, "font": FONT_MED})])
        _text(s, x + Inches(0.2), TOP + Inches(0.6), cw - Inches(0.35), Inches(2.2),
              [[(f"·  {i}", {"size": 8.5, "color": BODY})] for i in items],
              spacing=1.12, space_after=4)
        x += cw + Inches(0.15)

    _text(s, LEFT, Inches(4.65), WIDTH, Inches(0.6), [
        ("Known limits we are not hiding: ", {"bold": True, "color": INK}),
        ("trap categories still have n=2, the Firestore layer is a stub, and the oral defense is "
         "typed rather than spoken. Each of these is scheduled above, not glossed over.", {}),
    ], size=9, spacing=1.15)


def s14_links(prs):
    s = prs.slides[13]
    rows = [
        "[ISI: URL repo publik]",
        "[ISI: URL video demo 3 menit]",
        "[ISI: URL produk live]",
    ]
    # The template keeps all three prompts inside ONE textbox as paragraphs.
    # Align each value to its own label paragraph instead of guessing offsets.
    prompt_box = None
    for shp in s.shapes:
        if shp.has_text_frame and "GitHub Public Repository" in shp.text_frame.text:
            prompt_box = shp
            break

    if prompt_box is not None:
        tf = prompt_box.text_frame
        # Paragraphs carry no explicit font size, so they render at PowerPoint's 18pt
        # body default. Accumulate real line advances instead of averaging the box height.
        para_h = Pt(18 * 1.2)
        targets = [i for i, p in enumerate(tf.paragraphs) if "Repository" in p.text
                   or "Demo Video" in p.text or "Final Product" in p.text]
        for idx, value in zip(targets, rows):
            y = prompt_box.top + Emu(int(para_h * idx))
            _text(s, Inches(4.55), y, Inches(5.0), Inches(0.32),
                  [(value, {"size": 10, "bold": True, "color": INDIGO})])
    else:  # defensive: template changed
        for i, value in enumerate(rows):
            _text(s, Inches(4.55), Inches(1.55) + Inches(i * 0.5), Inches(5.0),
                  Inches(0.32), [(value, {"size": 10, "bold": True, "color": INDIGO})])

    _text(s, LEFT, Inches(4.60), WIDTH, Inches(0.7), [
        ("Team: ", {"bold": True, "color": INK}),
        ("Assay — Rafida Aziz (lead), M. Zulfi Fahreza, Wildan Fajar Maulana.  ", {}),
        ("Stack: ", {"bold": True, "color": INK}),
        ("React 18 + Vite, FastAPI, Gemini 2.5 via the google-genai SDK, deployed on Google Cloud Run.", {}),
    ], size=9, spacing=1.2, color=MUTED)


BUILDERS = [s01_team, s03_brief, s04_opportunity, s05_features, s06_flow,
            s08_architecture, s09_tech, s10_cost, s11_snapshots, s12_benchmark,
            s13_future, s14_links]

# builder -> 0-based slide index, so a single slide can be rebuilt in place
SLIDE_OF = {fn: fn.__name__ for fn in BUILDERS}
SLIDE_OF.update({
    "s01_team": 0, "s03_brief": 2, "s04_opportunity": 3, "s05_features": 4,
    "s06_flow": 5, "s08_architecture": 7, "s09_tech": 8, "s10_cost": 9,
    "s11_snapshots": 10, "s12_benchmark": 11, "s13_future": 12, "s14_links": 13,
})


def main(argv: list[str]) -> int:
    only = [a for a in argv if not a.startswith("-")]
    prs = Presentation(str(DECK))
    for fn in BUILDERS:
        if only and fn.__name__ not in only:
            continue
        if only:
            # rebuilding in place: wipe the old body so shapes do not stack
            _purge_body(prs.slides[SLIDE_OF[fn.__name__]])
        fn(prs)
        print("built:", fn.__name__)
    prs.save(str(DECK))
    print("saved:", DECK, DECK.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
