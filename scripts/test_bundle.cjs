// Exercise the actual patched bundle with populated advertising responses.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const dir = process.argv[2];
function chunk(id) {
  const names = fs.readdirSync(dir).filter(n => n.startsWith(`${id}.`) && n.endsWith('.js'));
  assert.equal(names.length, 1, `Expected one chunk ${id}`);
  return fs.readFileSync(path.join(dir, names[0]), 'utf8');
}
function expression(source, pattern) {
  const match = source.match(pattern);
  assert.ok(match, `Bundle structure changed: ${pattern}`);
  return match[1];
}
const home = chunk(5840);
const detail = chunk(3276);
function checkCover(source) {
  const expr = expression(source, /Oe=(.*?),\[Me,Fe\]/);
  for (const Ie of [false, true]) {
    for (const img of [{}, {app_pop3_cover: {advs: [{}]}},
      {app_pop3_img: {advs: [{}]}},
      {app_pop3_cover: {advs: [{}]}, app_pop3_img: {advs: [{}]}}]) {
      const result = vm.runInNewContext(
        `var s,u,h,x,p,v,f,j,_,I; (${expr})`, {Ie, T: {adsContent: {img}}});
      assert.equal(result, false, 'Cold-start cover advert must stay disabled');
    }
  }
}
function checkDetail(source) {
  const input = expression(source, /Se=(.*?),Ae=/);
  const renderList = expression(source, /Ce=(.*?),Oe=/);
  const context = {
    Z: {stype: {app_detail_between_author_and_related: [
      {advs: [{adv_id: 'ci-ad', adv_title: 'CI advert', adv_name: 'CI'}]}
    ]}},
    l: {useMemo: fn => fn()},
    J: {g9: () => ({indexes: [0]})},
  };
  const count = vm.runInNewContext(
    `var t; const Se=${input}; (${renderList}).length`, context);
  assert.equal(count, 0, 'Description advertising list must remain empty');
}
checkCover(home);
checkDetail(detail);
// These checks must reject the two previously missed advertising paths.
assert.throws(() => checkCover(home.replace('Oe=!1&&', 'Oe=!Ie&&')),
  /Cold-start cover advert/);
assert.throws(() => checkDetail(detail.replace('Se=[]',
  'Se=Z.stype.app_detail_between_author_and_related')), /Description advertising/);
// Preserve the confirmation page and real comic description.
assert.ok(home.includes('modal.age_confirmation'));
assert.ok(home.includes('p||sessionStorage.setItem("state",JSON.stringify(!0))'));
assert.ok(detail.includes('X.description'));
assert.ok(!home.includes('modal.ad_close_hint'));
const splash = expression(home, /G=(.*?),V=e=>/);
let next = 0;
const render = vm.runInNewContext(`(${splash})`, {a: {useEffect: fn => fn()}});
assert.equal(render({onNext: () => next++}), null);
assert.equal(next, 1, 'Splash must advance without an X click');
console.log('Bundle behavior passed: splash, populated cover ads, description ads, preserved confirmation.');
