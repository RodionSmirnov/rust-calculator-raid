/* Counts per individual full-health target; vanilla explosive raiding. */
const targets = [
  { id: 'wood-door', name: 'Деревянная дверь', hp: 200, counts: [1, 1, 2] },
  { id: 'metal-door', name: 'Железная дверь', hp: 250, counts: [2, 1, 4] },
  { id: 'garage-door', name: 'Гаражная дверь', hp: 600, counts: [3, 2, 9] },
  { id: 'armored-door', name: 'Бронированная дверь', hp: 1000, counts: [4, 2, 12] },
  { id: 'wood-wall', name: 'Деревянная стена', hp: 250, counts: [2, 1, 3] },
  { id: 'stone-wall', name: 'Каменная стена', hp: 500, counts: [4, 2, 10] },
  { id: 'metal-wall', name: 'Металлическая стена', hp: 1000, counts: [8, 4, 23] },
  { id: 'armored-wall', name: 'Бронированная стена', hp: 2000, counts: [15, 8, 46] },
];
const weapons = [
  { name: 'Ракеты', sulfur: 1400, powder: 650 },
  { name: 'C4', sulfur: 2200, powder: 1000 },
  { name: 'Сачели', sulfur: 480, powder: 240 },
];
function calculate(rows, weaponIndex) {
  const weapon = weapons[weaponIndex];
  if (!weapon) throw new Error('Unknown weapon');
  const amount = rows.reduce((sum, row) => {
    const target = targets.find(target => target.id === row.target);
    if (!target || !Number.isInteger(row.quantity) || row.quantity < 1 || row.quantity > 1000) {
      throw new Error('Invalid target or quantity');
    }
    return sum + target.counts[weaponIndex] * row.quantity;
  }, 0);
  return { amount, sulfur: amount * weapon.sulfur, powder: amount * weapon.powder, charcoal: amount * weapon.powder * 3 };
}
if (typeof module !== 'undefined') module.exports = { targets, weapons, calculate };
