const $ = id => document.getElementById(id);
const format = value => value == null ? '—' : value.toLocaleString('ru-RU', {maximumFractionDigits: 2});
let catalog, rows = [{target: 'metal-door', quantity: 1, side: 'hard', damage: ''}], revision = 0;
let timer;
function renderRows() {
  $('targets').replaceChildren();
  rows.forEach((row, index) => {
    const target = catalog.targets.find(t => t.id === row.target);
    const container = document.createElement('div');
    container.className = 'target-row';
    container.innerHTML = `<div class="row-heading">ПРЕПЯТСТВИЕ ${index + 1}<button class="remove" aria-label="Удалить цель ${index + 1}" ${rows.length === 1 ? 'disabled' : ''}>×</button></div><div class="target-grid"><label class="target-select">Цель<select data-field="target">${catalog.targets.map(t => `<option value="${t.id}">${t.name} · ${t.hp} HP</option>`).join('')}</select></label><label>Количество<input data-field="quantity" type="number" min="1" max="1000" step="1"></label><label>Здоровье<input data-field="hp" type="number" min="0.01" max="${target.hp}" step="any"></label><label>Сторона<select data-field="side" ${target.wall ? '' : 'disabled'}><option value="hard">Твёрдая / снаружи</option><option value="soft">Мягкая / изнутри</option></select></label><label>Урон за 1 единицу<input data-field="damage" type="number" min="0" step="any" placeholder="По таблице / ввести"></label></div>`;
    container.querySelectorAll('[data-field]').forEach(input => {
      const field = input.dataset.field;
      input.value = row[field] ?? (field === 'hp' ? target.hp : '');
      input.addEventListener('change', () => {
        if (field === 'target') { row.target = input.value; delete row.hp; row.damage = ''; row.side = 'hard'; renderRows(); }
        else { row[field] = ['quantity', 'hp'].includes(field) ? Number(input.value) : input.value; if (field === 'side') { row.damage = ''; renderRows(); } }
        schedule();
      });
    });
    container.querySelector('.remove').onclick = () => { rows.splice(index, 1); renderRows(); schedule(); };
    $('targets').append(container);
  });
  $('add').disabled = rows.length >= 100;
}
function schedule() {
  revision++;
  clearTimeout(timer);
  for (const id of ['amount', 'sulfur', 'powder', 'charcoal']) $(id).textContent = '…';
  $('breakdown').replaceChildren();
  timer = setTimeout(update, 100);
}
async function update() {
  const current = revision;
  const payload = {weapon: $('weapon').value, rows, resources: {}};
  for (const key of ['sulfur', 'powder']) if ($('unit-' + key).value !== '') payload.resources[key] = $('unit-' + key).value;
  try {
    const response = await fetch('/api/calculate', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const data = await response.json();
    if (current !== revision) return;
    if (!response.ok) throw new Error(data.error);
    $('error').hidden = true;
    for (const id of ['amount', 'sulfur', 'powder', 'charcoal']) $(id).textContent = format(data[id]);
    $('weapon-name').textContent = data.weapon;
    $('missing').textContent = data.missing.length ? 'Нужен урон по цели: ' + [...new Set(data.missing)].join(', ') : '';
    $('breakdown').replaceChildren();
    data.details.forEach(detail => {
      const tr = document.createElement('tr');
      for (const value of [detail.target, detail.quantity, detail.per_target, detail.amount]) {
        const td = document.createElement('td'); td.textContent = typeof value === 'string' ? value : format(value); tr.append(td);
      }
      $('breakdown').append(tr);
    });
    try { localStorage.setItem('rust-raid-python', JSON.stringify({...payload, note: $('profile-note').value})); } catch (_) { /* Storage may be unavailable. */ }
  } catch (error) {
    if (current !== revision) return;
    for (const id of ['amount', 'sulfur', 'powder', 'charcoal']) $(id).textContent = '—';
    $('missing').textContent = '';
    $('error').textContent = 'Не удалось рассчитать: ' + error.message;
    $('error').hidden = false;
  }
}
function weaponNote() {
  const weapon = catalog.weapons.find(w => w.id === $('weapon').value);
  $('weapon-note').textContent = weapon.counts ? 'Базовая таблица для целей с полным HP. ' + weapon.note : weapon.note + ' Нулевой урон не даёт конечного результата.';
  for (const key of ['sulfur', 'powder']) $('unit-' + key).placeholder = weapon.counts ? String(weapon[key]) : 'Неизвестно';
}
async function init() {
  try {
    const response = await fetch('/api/catalog');
    if (!response.ok) throw new Error('Сервер недоступен');
    catalog = await response.json();
    for (const category of [...new Set(catalog.weapons.map(w => w.category))]) {
      const group = document.createElement('optgroup'); group.label = category;
      catalog.weapons.filter(w => w.category === category).forEach(w => { const option = document.createElement('option'); option.value = w.id; option.textContent = w.name; group.append(option); });
      $('weapon').append(group);
    }
    try {
      const saved = JSON.parse(localStorage.getItem('rust-raid-python'));
      if (saved && catalog.weapons.some(w => w.id === saved.weapon) && Array.isArray(saved.rows) && saved.rows.length && saved.rows.length <= 100 && saved.rows.every(r => catalog.targets.some(t => t.id === r.target))) {
        rows = saved.rows; $('weapon').value = saved.weapon; $('profile-note').value = saved.note || '';
        for (const key of ['sulfur', 'powder']) $('unit-' + key).value = saved.resources?.[key] ?? '';
      }
    } catch (_) { /* Start with default plan. */ }
    renderRows(); weaponNote(); schedule();
  } catch (error) { $('error').hidden = false; $('error').textContent = 'Запусти python3 server.py и открой сайт через сервер. ' + error.message; }
}
$('add').onclick = () => { if (rows.length >= 100) return; rows.push({target: 'stone-wall', quantity: 1, side: 'hard', damage: ''}); renderRows(); schedule(); };
$('weapon').onchange = () => { rows.forEach(r => r.damage = ''); $('unit-sulfur').value = ''; $('unit-powder').value = ''; renderRows(); weaponNote(); schedule(); };
for (const id of ['unit-sulfur', 'unit-powder', 'profile-note']) $(id).addEventListener('input', schedule);
init();
