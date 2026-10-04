#!/usr/bin/env python3
"""Programmatic box-drawing engine + shared CSS for the TUI-styled SIH PDF.

Every diagram is composed from Box objects so borders always line up.
"""
import textwrap

CLR = {"term": "#00e5a0", "info": "#58a6ff", "warn": "#ffb454",
       "bad": "#ff5f56", "dim": "#5c6b7d", "key": "#c9d5e3"}
EDGE = "#22303f"
DIM = f'<span style="color:{EDGE}">%s</span>'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Box:
    def __init__(self, title, sub=None, color="term", width=None, icon=None):
        self.color = color
        self.title = title.upper()
        subs = sub.split("\n") if sub else []
        self.subs = subs
        need = max([len(self.title)] + [len(s) for s in subs] + [3])
        self.inner = need + 2
        if width:
            self.inner = max(self.inner, width + 2)
        if self.inner % 2:
            self.inner += 1
        self.icon = icon

    def rows(self):
        pad = " " + (self.icon + " " if self.icon else "")
        t = (pad + self.title)[: self.inner - 1]
        out = ["┌" + "─" * self.inner + "┐", "│" + t.ljust(self.inner) + "│"]
        for s in self.subs:
            out.append("│" + (" " + s)[: self.inner].ljust(self.inner) + "│")
        out.append("└" + "─" * self.inner + "┘")
        return out

    @property
    def height(self):
        return len(self.rows())

    @property
    def width(self):
        return self.inner + 2

    @property
    def cx(self):
        return self.inner // 2 + 1

    def render(self):
        return [f'<span style="color:{CLR[self.color]}">{esc(r)}</span>' for r in self.rows()]


def chain(boxes, sep="  ", color="#00e5a0"):
    """Boxes side by side, vertically centred, joined by an arrow on the middle row."""
    h = max(b.height for b in boxes)
    cols = []
    for b in boxes:
        pad = (h - b.height) // 2
        cols.append([""] * pad + b.render() + [""] * (h - b.height - pad))
    out, mid = [], h // 2
    for r in range(h):
        seg = []
        for i, b in enumerate(boxes):
            seg.append(cols[i][r])
            if i < len(boxes) - 1:
                seg.append(f'<span style="color:{color}">{sep if r == mid else " " * len(sep)}</span>')
        out.append("".join(seg))
    return out


def down_from(boxes, sep="", connector=1):
    """Connector/arrow rows aligned under the given boxes, matching a chain's `sep`."""
    n = len(boxes)
    x = lambda i: sum(b.width for b in boxes[:i]) + i * len(sep)
    width = x(n - 1) + boxes[-1].width
    c1, c2 = [" "] * width, [" "] * width
    for i, b in enumerate(boxes):
        cx = x(i) + b.cx
        c1[cx] = "│"
        c2[cx] = "▼"
    out = [DIM % "".join(c1)]
    out += [DIM % "".join(c2) for _ in range(connector)]
    return out


def up_to(boxes):
    a = [" "] * (sum(b.width for b in boxes) + 4 * (len(boxes) - 1))
    for b in boxes:
        x = sum(x.width + 4 for x in boxes[:boxes.index(b)])
        a[x + b.cx] = "▲"
    return [DIM % "".join(a)]


def panel(label, body_lines, color="dim", width=100):
    inner = width - 2
    out = [DIM % ("╒" + "═" * inner + "╕")]
    for ln in body_lines:
        out.append(DIM % "│" + f'<span style="color:{CLR[color]}">{(ln[:inner]).ljust(inner)}</span>' + DIM % "│")
    out.append(DIM % ("╘" + "═" * inner + "╛"))
    return out


def timeline(labels, captions, inner=9, label="week"):
    """Horizontal week timeline: header, connected boxes, wrapped captions."""
    n = len(labels)
    cells, hdr, caps = [], [], []
    for i in range(n):
        t = (" " + labels[i].upper())[:inner]
        cells.append("│" + '<span style="color:%s">%s</span>' % (CLR["key"], t.center(inner)) + "│")
        hdr.append('<span style="color:#00e5a0">%s</span>' % str(i + 1).rjust(inner - 1))
    tl = "   " + f'<span style="color:#5c6b7d">{label}</span>' + "".join(hdr)
    b1 = "  " + "┌" + "─" * inner + "".join("─" * inner + ("┬" if i < n - 1 else "┐") for i in range(n - 1))
    mid = "  " + "".join(cells)
    b2 = "  " + "└" + "─" * inner + "".join("─" * inner + ("┴" if i < n - 1 else "┘") for i in range(n - 1))
    ncap, cols = 0, []
    for c in captions:
        w = (textwrap.wrap(c, inner, break_long_words=False, break_on_hyphens=False) or [""])[:3]
        cols.append(w)
        ncap = max(ncap, len(w))
    cap_rows = []
    for r in range(ncap):
        seg = []
        for i in range(n):
            txt = cols[i][r] if r < len(cols[i]) else ""
            seg.append('<span style="color:#5c6b7d">%s</span>' % txt.center(inner))
            if i < n - 1:
                seg.append('<span style="color:#5c6b7d">·</span>')
        cap_rows.append("   " + "".join(seg))
    return [tl, b1, mid, b2] + cap_rows


def flow(lines):
    return '<pre class="flow">' + "\n".join(lines) + "</pre>"

def roster(rows, width=112, label_col=4):
    """Compact TUI roadmap roster:  wk  build  ->  done when."""
    out = []
    w1 = 56
    w2 = width - label_col - w1 - 6
    hdr = (DIM % " " * label_col) + f'<span style="color:#5c6b7d">{"build".ljust(w1)}  done when</span>'
    out.append(hdr)
    for wk, build, done in rows:
        b = (textwrap.wrap(build, w1 - 2) or [""])
        d = (textwrap.wrap(done, w2 - 2) or [""])
        n = max(len(b), len(d))
        for i in range(n):
            bt = b[i] if i < len(b) else ""
            dt = d[i] if i < len(d) else ""
            cell = f'<span style="color:#c9d5e3">{bt.ljust(w1)}</span>'
            if dt:
                cell += f'<span style="color:#00e5a0">→ </span><span style="color:#8b98a8">{dt}</span>'
            if i == 0:
                out.append(f'<span style="color:#00e5a0">{wk.rjust(2)}</span> ' + cell)
            else:
                out.append(" " * (label_col - 1) + " " + cell)
    return out
