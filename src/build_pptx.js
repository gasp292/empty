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

function header(slide, title, sub) {
  slide.background = { color: 'FFFFFF' };
  slide.addText(title, { x: 0.5, y: 0.25, w: 9, h: 0.5, fontFace: FONT, fontSize: 26, bold: true, color: P.ink, margin: 0, isTextBox: true });
  slide.addText(sub, { x: 9.3, y: 0.3, w: 3.53, h: 0.4, fontFace: FONT, fontSize: 12, color: P.muted, align: 'right', margin: 0, isTextBox: true });
}

function drawDiagram(slide, d, box, fs) {
  const sx = box.w / d.w, sy = box.h / d.h;
  const X = x => box.x + x * sx, Y = y => box.y + y * sy;
  // flèches (segments) d'abord, pour passer sous les boîtes
  for (const e of d.edges) {
    const color = CAT[e.cls] || P.line_strong;
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
    const textColor = sys ? 'FFFFFF' : P.ink;
    const runs = lines.map((t, i) => ({
      text: t,
      options: {
        bold: sys || fn || (!sub && lines.length > 1 && i === 0),
        color: (!sys && !fn && !sub && i > 0) ? P.muted : textColor,
        breakLine: i < lines.length - 1,
      },
    }));
    const stroke = sys ? P.ink : fn ? P.accent : (CAT[n.cls] || P.line_strong);
    const line = { color: stroke, width: n.cls.startsWith('c-') ? 1.75 : 1 };
    if (n.cls === 'sec') line.dashType = 'dash';
    slide.addText(runs, {
      shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.06,
      x: X(n.cx - n.w / 2), y: Y(n.cy - n.h / 2), w: n.w * sx, h: n.h * sy,
      fill: { color: sys ? P.ink : fn ? P.fn : 'FFFFFF' }, line,
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
      fontFace: FONT, fontSize: fs.label, color: P.muted, align: 'center', valign: 'middle',
      fill: { color: 'FFFFFF' }, margin: 0, isTextBox: true,
    });
  }
  for (const [x, y, t] of d.texts || []) {
    slide.addText(t, { x: X(x) - 1.5, y: Y(y) - 0.15, w: 3, h: 0.3, fontFace: FONT, fontSize: 12, bold: true,
      color: P.ink, align: 'center', valign: 'middle', charSpacing: 2, margin: 0, isTextBox: true });
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
header(s, 'Environment analysis', 'Operational view · Environment diagram');
drawDiagram(s, M.env, { x: 0.5, y: 0.85, w: 12.33, h: 6.4 }, { sys: 13, fn: 9, node: 8, label: 7 });
s.addNotes('Delivery drone as a black box. 18 external actors and systems (2 secondary), grouped in the four categories of the course: constraints, structuring inputs, structuring outputs, resources.');

// 2. Functional breakdown structure
s = pres.addSlide();
header(s, 'Functional breakdown structure', 'Functional view · Behavioral analysis');
drawDiagram(s, M.fbs, { x: 0.5, y: 1.0, w: 12.33, h: 6.1 }, { sys: 12, fn: 9, node: 7.5, label: 7 });
s.addNotes('F0 is the mission. 8 level-1 functions and 42 level-2 sub-functions. Every function starts with an action verb and names no technology.');

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

pres.writeFile({ fileName: path.join(__dirname, '..', 'livrables', 'drone_mbse_EN.pptx') }).then(f => console.log('written', f));
