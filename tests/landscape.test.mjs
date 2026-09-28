// Tests for the landing-page art (docs/_static/landscape.js). Run: node --test tests/landscape.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { plan, DT } from "../docs/_static/landscape.js";

const SIZES = [[1440, 450], [390, 420]]; // desktop band, phone band (px)

// The curve's lowest point on screen (SVG y grows downward, so: largest y).
function globalMinX(f, W) {
  let best = 0;
  for (let x = 0; x <= W; x += 0.5) if (f(x) > f(best)) best = x;
  return best;
}

test("ball always settles at the nearest ridge's global minimum", () => {
  for (const [W, H] of SIZES) {
    for (let seed = 1; seed <= 150; seed++) {
      const { ridges, frames, r } = plan(seed, W, H);
      const near = ridges.at(-1);
      const end = frames.at(-1);
      assert.ok(Math.abs(end.x - globalMinX(near.y, W)) < r / 2, `seed ${seed} at ${W}x${H}: stopped at x=${end.x.toFixed(1)}`);
    }
  }
});

test("ball stays on screen, never sinks into the ridge, and settles in time", () => {
  for (const [W, H] of SIZES) {
    for (let seed = 1; seed <= 150; seed++) {
      const { ridges, frames, r } = plan(seed, W, H);
      const near = ridges.at(-1);
      for (const { x, y } of frames) {
        assert.ok(x >= r && x <= W - r, `seed ${seed}: x=${x} off screen`);
        assert.ok(y + r <= near.y(x) + 1.5, `seed ${seed}: sank into the ridge at x=${x}`);
      }
      assert.ok(frames.length * DT < 12, `seed ${seed}: took ${(frames.length * DT).toFixed(1)} s`);
    }
  }
});

test("same seed gives the same scene; different seeds differ", () => {
  const a = plan(7, 1440, 450), b = plan(7, 1440, 450), c = plan(8, 1440, 450);
  assert.deepEqual(a.frames, b.frames);
  assert.notEqual(a.ridges[2].y(700), c.ridges[2].y(700));
});
