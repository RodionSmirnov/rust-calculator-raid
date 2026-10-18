let rows = [{ target: 'metal-door', quantity: 1 }];
let selectedWeapon = 0;
const format = value => value.toLocaleString('ru-RU');
function renderRows() {
  document.getElementById('targets').innerHTML = rows.map((row, index) => `<div class="target-row"><label>Препятствие<select data-index="${index}" aria-label="Препятствие ${index + 1}">${targets.map(target => `<option value="${target.id}" ${row.target === target.id ? 'selected' : ''}>${target.name} · ${target.hp} HP</option>`).join('')}</select></label><label>Кол-во<input aria-label="Количество ${index + 1}" type="number" min="1" max="1000" step="1" value="${row.quantity}" data-index="${index}"></label><button class="remove" data-remove="${index}" aria-label="Удалить цель ${index + 1}" ${rows.length === 1 ? 'disabled' : ''}>×</button></div>`).join('');
}
function update() {
  const result = calculate(rows, selectedWeapon);
  for (const key of ['amount', 'sulfur', 'powder', 'charcoal']) document.getElementById(key).textContent = format(result[key]);
  document.getElementById('weapon-name').textContent = weapons[selectedWeapon].name;
  document.getElementById('weapons').innerHTML = weapons.map((weapon, index) => `<button data-weapon="${index}" aria-pressed="${index === selectedWeapon}" class="${index === selectedWeapon ? 'active' : ''}">${weapon.name}</button>`).join('');
  document.getElementById('comparison').innerHTML = weapons.map((weapon, index) => {
    const value = calculate(rows, index);
    return `<tr class="${index === selectedWeapon ? 'selected' : ''}"><td>${weapon.name}</td><td>${format(value.amount)}</td><td>${format(value.sulfur)}</td><td>${format(value.powder)}</td></tr>`;
  }).join('');
}
document.getElementById('targets').addEventListener('change', event => {
  const index = Number(event.target.dataset.index);
  if (event.target.tagName === 'SELECT') rows[index].target = event.target.value;
  if (event.target.tagName === 'INPUT') {
    const value = Number(event.target.value);
    rows[index].quantity = Number.isFinite(value) ? Math.max(1, Math.min(1000, Math.floor(value))) : 1;
    event.target.value = rows[index].quantity;
  }
  update();
});
document.getElementById('targets').addEventListener('click', event => {
  if (event.target.dataset.remove !== undefined && rows.length > 1) { rows.splice(Number(event.target.dataset.remove), 1); renderRows(); update(); }
});
document.getElementById('add').onclick = () => { rows.push({ target: 'stone-wall', quantity: 1 }); renderRows(); update(); };
document.getElementById('weapons').onclick = event => { if (event.target.dataset.weapon !== undefined) { selectedWeapon = Number(event.target.dataset.weapon); update(); } };
renderRows(); update();
