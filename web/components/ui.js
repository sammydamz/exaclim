import '@awesome.me/webawesome/dist/styles/themes/default.css';
import '@awesome.me/webawesome/dist/components/card/card.js';
import '@awesome.me/webawesome/dist/components/badge/badge.js';
import '@ui-sdk/web/button';
import '@ui-sdk/web/tabs';
import '@ui-sdk/web/field';
import '@ui-sdk/web/input';
import '@ui-sdk/web/select';
import '@ui-sdk/web/dialog';
import '@ui-sdk/web/toast';
export { toast } from '@ui-sdk/web';
import { createAgent } from '@ui-sdk/web/agent';

export const agent = createAgent();
export function onAction(selector, callback) {
  const button = typeof selector === 'string' ? document.querySelector(selector) : selector;
  const root = button.closest('ui-button');
  root.addEventListener('action', event => event.detail.waitUntil(Promise.resolve(callback(event))));
}
export function inputValue(id) {
  const root = document.getElementById(id);
  return root?.api?.getValue?.() ?? root?.value ?? '';
}
export function setInput(id, value) {
  const root = document.getElementById(id);
  if (root?.api?.setValue) root.api.setValue(value);
  else if (root) root.value = value;
}
export function setSelect(id, items, value) {
  const root = document.getElementById(id);
  root.items = items;
  root.querySelector('ui-select-content').replaceChildren(...items.map(item => {
    const node = document.createElement('ui-select-item');
    node.setAttribute('value', item.value);
    node.textContent = item.label;
    return node;
  }));
  root.value = value ?? items[0]?.value ?? null;
}
export const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
