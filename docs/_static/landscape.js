// Landing-page art: a random loss landscape, new on every visit, and a soccer
// ball (a truncated icosahedron, i.e. C60) that bounces down it and settles at
// the global minimum. plan() is pure and tested (tests/landscape.test.mjs);
// mount() only runs in a browser, on Shibuya's landing layout.

export const DT = 1 / 120; // s, simulation step
const G = 1800; // px/s², gravity
const BOUNCE = 0.5; // share of the normal speed kept at each bounce
const ROLL = 90; // px/s: a bounce slower than this turns into rolling
const DRAG = 0.8; // 1/s, viscous rolling friction
const GRIP = 30; // px/s², rolling resistance: lets the ball actually stop
const T_MAX = 11; // s: slower runs are rejected

// Seeded PRNG (mulberry32): one seed reproduces one scene exactly.
function rng(seed) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// A ridge is a 1-D loss curve: a bowl rising to both edges plus random ripples
// with amplitude ~ 1/frequency. y(x), dy(x) in SVG px (y grows downward, so
// the minimum is the largest y). depth 0 is the farthest ridge, 2 the nearest.
function ridge(rand, W, H, depth) {
  const base = H * (0.49 + 0.14 * depth);
  const bowl = H * (0.17 - 0.025 * depth);
  const amp = H * (0.09 - 0.02 * depth);
  const fmax = Math.max(3, (13 * W) / 1600); // shortest ripple ~120 px on any screen
  const waves = Array.from({ length: 9 }, () => [1 + rand() * fmax, rand() * 2 * Math.PI]);
  const y = (x) => {
    const t = x / W;
    return base - bowl * (2 * t - 1) ** 2 - amp * waves.reduce((s, [f, p]) => s + Math.sin(2 * Math.PI * f * t + p) / f, 0);
  };
  const dy = (x) => {
    const t = x / W;
    return (-4 * bowl * (2 * t - 1) - 2 * Math.PI * amp * waves.reduce((s, [f, p]) => s + Math.cos(2 * Math.PI * f * t + p), 0)) / W;
  };
  return { y, dy };
}

// Drop a ball of radius r above x0 and integrate until it rests. Returns frames
// [{x, y, a}] (centre in px, spin in degrees), or null if it left the screen or
// took too long.
function simulate({ y: s, dy }, W, r, x0) {
  const touch = (x) => s(x) - r * Math.hypot(1, dy(x)); // centre height when resting on the ridge
  let x = x0, y = -2 * r, vx = 0, vy = 0, a = 0, spin = 0;
  let v = null; // speed along the ridge once rolling
  const frames = [];
  for (let t = 0; t < T_MAX; t += DT) {
    if (v === null) {
      // In flight: gravity, then bounce off the ridge (reflect the normal
      // velocity with restitution, keep the tangential part).
      vy += G * DT;
      x += vx * DT;
      y += vy * DT;
      a += spin * DT;
      if (y >= touch(x)) {
        const k = dy(x), n = Math.hypot(1, k);
        const vt = (vx + vy * k) / n; // along the ridge
        const vn = (vx * k - vy) / n; // out of the ridge (negative: into it)
        y = touch(x);
        spin = ((vt / r) * 180) / Math.PI;
        if (-vn < ROLL) v = vt;
        else {
          const out = -BOUNCE * vn;
          vx = (vt + out * k) / n;
          vy = (vt * k - out) / n;
        }
      }
    } else {
      // Rolling: gravity along the slope, minus drag and rolling resistance.
      const k = dy(x), n = Math.hypot(1, k), pull = (G * k) / n;
      if (Math.abs(v) < GRIP * DT * 2 && Math.abs(pull) < GRIP) {
        frames.push({ x, y, a });
        return frames; // at rest
      }
      v += (pull - DRAG * v - GRIP * Math.sign(v)) * DT;
      x += (v / n) * DT;
      y = touch(x);
      a += ((v / r) * DT * 180) / Math.PI;
    }
    if (x < r || x > W - r) return null;
    frames.push({ x, y, a });
  }
  return null;
}

// A scene for a W×H px band: three ridges and the ball's path. Landscapes where
// the ball would stop in a local minimum are redrawn, so it always ends at the
// nearest ridge's global minimum.
export function plan(seed, W, H) {
  const rand = rng(seed);
  const r = Math.max(10, Math.min(14, H * 0.03));
  let ridges, near, lowest;
  for (let tries = 0; tries < 300; tries++) {
    ridges = [0, 1, 2].map((depth) => ridge(rand, W, H, depth));
    near = ridges[2];
    lowest = 0;
    for (let x = 0; x <= W; x += 0.5) if (near.y(x) > near.y(lowest)) lowest = x;
    const side = rand() < 0.5 ? 0.06 : 0.8; // start high on one flank of the bowl
    const frames = simulate(near, W, r, (side + 0.14 * rand()) * W);
    if (frames && Math.abs(frames.at(-1).x - lowest) < r / 3) return { ridges, frames, r };
  }
  // ponytail: no landscape worked (only plausible on absurd sizes); show the ball at rest.
  const x = Math.min(Math.max(lowest, r), W - r);
  return { ridges, frames: [{ x, y: near.y(x) - r * Math.hypot(1, near.dy(x)), a: 0 }], r };
}

// ---------------------------------------------------------------- browser ---

const NS = "http://www.w3.org/2000/svg";
function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

// A classic soccer ball seen face-on around a pentagon: one central and five
// rim pentagons, joined by the seams of the hexagons between them.
function soccerBall(r, g, defs) {
  const penta = (cx, cy, R, rot) =>
    Array.from({ length: 5 }, (_, j) => [cx + R * Math.cos(rot + (j * 2 * Math.PI) / 5), cy + R * Math.sin(rot + (j * 2 * Math.PI) / 5)]);
  const dirs = [0, 1, 2, 3, 4].map((k) => -Math.PI / 2 + (k * 2 * Math.PI) / 5);
  const inner = penta(0, 0, 0.34 * r, dirs[0]);
  // Rim pentagon k: vertex 0 points at the centre; vertices 1 and 4 flank it.
  const rim = dirs.map((t) => penta(0.98 * r * Math.cos(t), 0.98 * r * Math.sin(t), 0.34 * r, t + Math.PI));
  const clip = el("clipPath", { id: "bp-ball-clip" }, defs);
  el("circle", { r }, clip);
  el("circle", { r, class: "bp-ball-skin" }, g);
  const art = el("g", { "clip-path": "url(#bp-ball-clip)" }, g);
  const pts = (p) => p.map(([x, y]) => `${x.toFixed(2)},${y.toFixed(2)}`).join(" ");
  const seam = ([x1, y1], [x2, y2]) => el("line", { x1, y1, x2, y2, class: "bp-ball-seam" }, art);
  for (const p of [inner, ...rim]) el("polygon", { points: pts(p), class: "bp-ball-patch" }, art);
  rim.forEach((p, k) => {
    seam(inner[k], p[0]); // centre pentagon to rim pentagon
    seam(p[4], rim[(k + 1) % 5][1]); // outer edge of the hexagon between them
  });
  el("circle", { r, class: "bp-ball-rim" }, g);
}

function mount() {
  const main = document.querySelector("main.sy-content"); // Shibuya's landing layout only
  if (!main) return;
  const svg = el("svg", { class: "bp-landscape", "aria-hidden": "true" });
  main.prepend(svg);
  const { width: W, height: H } = svg.getBoundingClientRect();
  const { ridges, frames, r } = plan((Math.random() * 2 ** 32) >>> 0, W, H);
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMax slice");
  const defs = el("defs", {}, svg);

  ridges.forEach(({ y }, k) => {
    let d = `M0 ${H}`, top = H;
    for (let x = 0; x <= W + 4; x += 4) {
      const yx = y(Math.min(x, W));
      top = Math.min(top, yx);
      d += `L${Math.min(x, W)} ${yx.toFixed(1)}`;
    }
    // Ink wash: dense at the crest, dissolving into mist below.
    const grad = el("linearGradient", { id: `bp-ink-${k}`, gradientUnits: "userSpaceOnUse", x1: 0, y1: top, x2: 0, y2: H }, defs);
    el("stop", { offset: 0, style: `stop-color: var(--bp-ink); stop-opacity: var(--bp-ridge-${k})` }, grad);
    el("stop", { offset: 1, style: "stop-color: var(--bp-ink); stop-opacity: 0" }, grad);
    el("path", { d: `${d}L${W} ${H}Z`, fill: `url(#bp-ink-${k})`, class: `bp-ridge bp-ridge-${k}` }, svg);
  });

  const ball = el("g", { class: "bp-ball" }, svg);
  soccerBall(r, ball, defs);
  const end = frames.at(-1);
  const label = el("text", { x: end.x, y: end.y - r - 10, class: "bp-label" }, svg);
  label.append("∇");
  el("tspan", { "font-style": "italic" }, label).append("L");
  label.append(" = 0");

  const show = ({ x, y, a }) => ball.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${a.toFixed(1)})`);
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    show(end);
    svg.classList.add("bp-done");
    return;
  }
  show(frames[0]);
  const DELAY = 0.9; // s: let the ridges rise first
  let t0;
  const tick = (now) => {
    t0 ??= now;
    const i = Math.floor(((now - t0) / 1000 - DELAY) / DT);
    show(frames[Math.min(Math.max(i, 0), frames.length - 1)]);
    if (i < frames.length) requestAnimationFrame(tick);
    else svg.classList.add("bp-done");
  };
  requestAnimationFrame(tick);
}

if (typeof document !== "undefined") mount();
