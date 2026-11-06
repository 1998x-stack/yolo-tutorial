const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'local-navigation.js'), 'utf8');
function element(tag) {
  return { tag, children: [], set textContent(value) { this.children = []; this._text = value; }, get textContent() { return this._text; }, appendChild(child) { this.children.push(child); } };
}
function setup() {
  const window = {};
  vm.runInNewContext(source, { window, document: { createElement: element }, Number, String });
  return window.renderOfflineChapters;
}
test('offline navigation renders all 28 local chapter links', () => {
  const root = element('div');
  setup()(root, 28);
  assert.equal(root.children.length, 29);
  assert.equal(root.children[1].children[0].href, '01.html');
  assert.equal(root.children[28].children[0].href, '28.html');
});
test('rendering twice does not append duplicate chapter links', () => {
  const root = element('div');
  const render = setup();
  render(root, 28);
  render(root, 28);
  assert.equal(root.children.length, 29);
});
test('invalid chapter count is rejected', () => {
  const render = setup();
  assert.throws(() => render(element('div'), 0), /Invalid offline/);
  assert.throws(() => render(element('div'), 100), /Invalid offline/);
});
