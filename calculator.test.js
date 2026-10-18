const { test } = require('node:test');
const assert = require('node:assert/strict');
const { calculate } = require('./calculator');
test('one sheet metal door with satchels includes all sulfur and charcoal', () => {
  assert.deepEqual(calculate([{ target: 'metal-door', quantity: 1 }], 2), { amount: 4, sulfur: 1920, powder: 960, charcoal: 2880 });
});
test('multiple distinct obstacles accumulate per-target rocket costs', () => {
  assert.deepEqual(calculate([{ target: 'metal-door', quantity: 2 }, { target: 'stone-wall', quantity: 1 }], 0), { amount: 8, sulfur: 11200, powder: 5200, charcoal: 15600 });
});
test('armored wall requires eight C4', () => assert.equal(calculate([{ target: 'armored-wall', quantity: 1 }], 1).amount, 8));
test('invalid quantities and targets are rejected', () => {
  for (const quantity of [0, -1, 1.5, NaN, 1001]) assert.throws(() => calculate([{ target: 'metal-door', quantity }], 0));
  assert.throws(() => calculate([{ target: 'unknown', quantity: 1 }], 0));
});
