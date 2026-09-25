// Génère livrables/drone_mbse_EN.pptx : diagrammes en formes natives PowerPoint (modifiables).
const pptxgen = require('pptxgenjs');
const path = require('path');
const M = require('./diagrams_en.json');
const P = M.palette;
const FONT = 'Calibri';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pres.title = 'Delivery drone - MBSE case study';

const CAT = { 'c-in': P.c_in, 'c-out': P.c_out, 'c-res': P.c_res, 'c-con': P.c_con, sec: P.sec, tree: P.line_strong };

function header(slide, title, sub, subtitle) {
  slide.background = { color: 'FFFFFF' };
  slide.addText(title, { x: 0.5, y: 0.25, w: 9, h: 0.5, fontFace: FONT, fontSize: 26, bold: true, color: P.ink, margin: 0, isTextBox: true });
  if (subtitle) slide.addText(subtitle, { x: 0.5, y: 0.75, w: 9, h: 0.3, fontFace: FONT, fontSize: 14, color: P.ink, margin: 0, isTextBox: true });
  slide.addText(sub, { x: 9.3, y: 0.3, w: 3.53, h: 0.4, fontFace: FONT, fontSize: 12, color: P.muted, align: 'right', margin: 0, isTextBox: true });
}

function drawDiagram(slide, d, box, fs, st = {}) {
  const sx = box.w / d.w, sy = box.h / d.h, dx = d.dx || 0;
  const X = x => box.x + (x + dx) * sx, Y = y => box.y + y * sy;
  // sous-systèmes et frontière du système
  const groups = d.groups || [];
  for (const g of groups) {
    const bnd = g.cls === 'bnd', gs = st[bnd ? 'bnd' : 'grp'] || {};
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: X(g.x0), y: Y(g.y0), w: (g.x1 - g.x0) * sx, h: (g.y1 - g.y0) * sy, rectRadius: bnd ? 0.15 : 0.04,
      fill: { color: gs.fill || P.grp }, line: { color: gs.fill || P.line, width: 0.75 },
    });
    if (bnd) {
      slide.addText(g.label, { x: X(g.x1) - 3.1, y: Y(g.y0) + 0.025, w: 3, h: 0.19, fontFace: FONT, fontSize: 12, bold: true,
        color: P.ink, align: 'right', valign: 'middle', margin: 0, isTextBox: true });
    } else {
      slide.addText(g.label, { x: X(g.lx), y: Y(g.y0) + 0.01, w: 1.6, h: 0.17, fontFace: FONT, fontSize: 8.5, bold: true,
        color: gs.text || P.muted, valign: 'middle', margin: 0, isTextBox: true });
    }
  }
  const bgAt = (x, y) => {  // couleur du fond sous un libellé
    let c = 'FFFFFF';
    for (const g of groups) if (x >= g.x0 && x <= g.x1 && y >= g.y0 && y <= g.y1) c = (st[g.cls === 'bnd' ? 'bnd' : 'grp'] || {}).fill || (g.cls === 'bnd' ? 'FFFFFF' : P.grp);
    return c;
  };
  // flèches (segments) d'abord, pour passer sous les boîtes
  for (const e of d.edges) {
    const color = st.flow || (e.cls === 'tree' && st.tree) || CAT[e.cls] || P.line_strong;
    const n = e.pts.length - 1;
    for (let i = 0; i < n; i++) {
      const [x1, y1] = e.pts[i], [x2, y2] = e.pts[i + 1];
      const line = { color, width: e.cls === 'tree' ? 1 : 1.25 };
      if (e.dash) line.dashType = 'dash';
      if (e.arrow && i === n - 1) line.endArrowType = 'triangle';
      if (e.arrow && e.both && i === 0) line.beginArrowType = 'triangle';
      slide.addShape(pres.shapes.LINE, {
        x: X(Math.min(x1, x2)), y: Y(Math.min(y1, y2)),
        w: Math.abs(x2 - x1) * sx, h: Math.abs(y2 - y1) * sy,
        flipH: x2 < x1, flipV: y2 < y1, line,
      });
    }
  }
  for (const n of d.nodes) {
    const lines = n.label.split('\n');
    const sys = n.cls === 'sys', fn = n.cls === 'fn', sub = n.cls === 'sub';
    const size = sys ? fs.sys : fn ? fs.fn : fs.node;
    const cs = st[n.cls];
    const textColor = cs ? cs.text : sys ? 'FFFFFF' : P.ink;
    const runs = lines.map((t, i) => ({
      text: t,
      options: {
        bold: sys || fn || (!sub && lines.length > 1 && i === 0),
        color: (!cs && !sys && !fn && !sub && i > 0) ? P.muted : textColor,
        breakLine: i < lines.length - 1,
      },
    }));
    const stroke = cs ? cs.fill : sys ? P.ink : fn ? P.accent : (CAT[n.cls] || P.line_strong);
    const line = { color: stroke, width: n.cls.startsWith('c-') ? 1.75 : 1 };
    if (n.cls === 'sec') line.dashType = 'dash';
    slide.addText(runs, {
      shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.06,
      x: X(n.cx - n.w / 2), y: Y(n.cy - n.h / 2), w: n.w * sx, h: n.h * sy,
      fill: { color: cs ? cs.fill : sys ? P.ink : fn ? P.fn : 'FFFFFF' }, line,
      fontFace: FONT, fontSize: size, align: 'center', valign: 'middle', margin: 2,
    });
  }
  for (const e of d.edges) {
    if (!e.label) continue;
    const lines = e.label.split('\n');
    const maxc = Math.max(...lines.map(l => l.length));
    const w = maxc * fs.label * 0.50 / 72 + 0.1, h = lines.length * fs.label * 1.2 / 72 + 0.05;
    slide.addText(lines.join('\n'), {
      x: X(e.lp[0]) - w / 2, y: Y(e.lp[1]) - h / 2, w, h,
      fontFace: FONT, fontSize: fs.label, color: st.flow ? P.ink : P.muted, align: 'center', valign: 'middle',
      fill: { color: bgAt(e.lp[0], e.lp[1]) }, margin: 0, isTextBox: true,
    });
  }
  for (const [x, y, t] of d.texts || []) {
    slide.addText(t, { x: X(x) - 1.5, y: Y(y) - 0.15, w: 3, h: 0.3, fontFace: FONT, fontSize: 12, bold: true,
      color: P.ink, align: 'center', valign: 'middle', charSpacing: 2, margin: 0, isTextBox: true });
  }
  for (const [[nx, ny], t] of d.notes || []) {
    slide.addText(t, { x: X(nx), y: Y(ny) - 0.1, w: 7, h: 0.2, fontFace: FONT, fontSize: 8, italic: true, color: P.muted,
      margin: 0, isTextBox: true });
  }
  if (d.legend && d.legend.length) {
    let [lx, ly] = d.legend_pos;
    for (const [c, lab] of d.legend) {
      const line = { color: CAT[c], width: 1.25, endArrowType: 'triangle' };
      if (c === 'sec') line.dashType = 'dash';
      slide.addShape(pres.shapes.LINE, { x: X(lx), y: Y(ly), w: 28 * sx, h: 0, line });
      slide.addText(lab, { x: X(lx + 34), y: Y(ly) - 0.1, w: 1.4, h: 0.2, fontFace: FONT, fontSize: 8, color: P.ink,
        valign: 'middle', margin: 0, isTextBox: true });
      lx += 50 + lab.length * 6.6;
    }
  }
}

// 1. Environment diagram
let s = pres.addSlide();
header(s, 'Environment analysis', 'Operational view · Environment analysis', 'Environment diagram');
drawDiagram(s, M.env, { x: 0.5, y: 1.05, w: 12.33, h: 6.25 }, { sys: 13, fn: 9, node: 8, label: 7 });
s.addNotes('Delivery drone as a black box. 18 external actors and systems (2 secondary), grouped in the four categories of the course: constraints, structuring inputs, structuring outputs, resources.');

// 2. Functional breakdown structure
s = pres.addSlide();
header(s, 'Functional analysis', 'Functional view · Behavioral analysis', 'Functional breakdown structure');
drawDiagram(s, M.fbs, { x: 0.5, y: 1.2, w: 12.33, h: 6.0 }, { sys: 13, fn: 9, node: 7.5, label: 7 }, {
  tree: '1F6FA3',
  sys: { fill: '00587C', text: 'FFFFFF' },
  fn: { fill: 'E1002A', text: 'FFFFFF' },
  sub: { fill: '9E3200', text: 'FFFFFF' },
});
s.addNotes('The root is the system of interest (delivery drone). 8 level-1 functions and 42 level-2 sub-functions. Every function starts with an action verb and names no technology.');

// 3. Coverage check
s = pres.addSlide();
header(s, 'Coverage check', 'Environment flows → functions');
const hdr = ['Category', 'External actor / system', 'Flow with the drone', 'Covered by functions'].map(t => ({
  text: t, options: { bold: true, color: 'FFFFFF', fill: { color: P.ink } } }));
const catColor = { Constraint: P.c_con, Input: P.c_in, Output: P.c_out, Resource: P.c_res };
const rows = M.coverage.map(([c, a, f, fs], i) => [
  { text: c, options: { color: catColor[c], bold: true } }, { text: a }, { text: f, options: { color: P.muted } },
  { text: fs, options: { color: P.accent, bold: true } }]);
s.addTable([hdr, ...rows], {
  x: 0.5, y: 1.0, w: 12.33, colW: [1.5, 3.4, 4.7, 2.73], rowH: 0.33,
  fontFace: FONT, fontSize: 11, color: P.ink, valign: 'middle',
  border: { type: 'solid', pt: 0.75, color: P.line }, margin: [0, 6, 0, 6],
});
s.addText('All 16 direct interactions are covered by at least one sub-function. Secondary systems (customer, energy grid) have no direct exchange with the drone.',
  { x: 0.5, y: 6.75, w: 12.33, h: 0.35, fontFace: FONT, fontSize: 11, italic: true, color: P.muted, margin: 0, isTextBox: true });

// 4. Technical interaction diagram
s = pres.addSlide();
header(s, 'Technical analysis', 'Technical view · Structural analysis', 'Technical interaction diagram');
drawDiagram(s, M.tech, { x: 0.5, y: 1.15, w: 12.33, h: 6.2 }, { sys: 12, fn: 9, node: 7.5, label: 7 }, {
  flow: '2E75B6',
  bnd: { fill: 'D9D9D9' },
  grp: { fill: '2FA84F', text: 'FFFFFF' },
  cmp: { fill: '1B5E36', text: 'FFFFFF' },
  ext: { fill: '0B6FB0', text: 'FFFFFF' },
});
s.addNotes('24 components in 8 sub-systems embody the 42 functions. Flows: electricity, data and signals, mechanical loads and matter, waves (light, sound, radio).');

// 5. Components -> functions
s = pres.addSlide();
header(s, 'Components → functions', 'Technical view · Traceability', 'Each component embodies at least one function; each function has at least one component');
const th = ['Component', 'Sub-system', 'Functions'].map(t => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: '1B5E36' } } }));
const half = Math.ceil(M.comp_trace.length / 2);
[M.comp_trace.slice(0, half), M.comp_trace.slice(half)].forEach((part, k) => {
  s.addTable([th, ...part.map(([c, g, f]) => [{ text: c, options: { bold: true } }, { text: g, options: { color: P.muted } },
    { text: f, options: { color: P.accent } }])], {
    x: 0.5 + k * 6.315, y: 1.3, w: 6.015, colW: [2.2, 1.25, 2.565], rowH: 0.42,
    fontFace: FONT, fontSize: 10, color: P.ink, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: P.line }, margin: [0, 5, 0, 5],
  });
});

pres.writeFile({ fileName: path.join(__dirname, '..', 'livrables', 'drone_mbse_EN.pptx') }).then(f => console.log('written', f));
