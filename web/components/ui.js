import '@ui-sdk/web/button';
import '@ui-sdk/web/tabs';
import '@ui-sdk/web/field';
import '@ui-sdk/web/input';
import '@ui-sdk/web/select';
import '@ui-sdk/web/dialog';
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
export const icon = (name, className = '') => {
  const paths = {
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    chevron: '<path d="m6 9 6 6 6-6"/>',
    settings: '<path d="M12 8v8m-4-4h8"/><circle cx="12" cy="12" r="9"/>',
    arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    shield: '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/>',
    warning: '<path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5m0 3v.1"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    pin: '<path d="M19 10c0 6-7 11-7 11S5 16 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
    help: '<path d="M12 7v6m0 4v.1"/><circle cx="12" cy="12" r="9"/>',
    link: '<path d="m9 15 6-6m-8 4-2 2a4 4 0 0 0 6 6l4-4m-2-10 2-2a4 4 0 0 1 6 6l-4 4"/>',
    close: '<path d="m6 6 12 12M6 18 18 6"/>',
    people: '<circle cx="9" cy="8" r="3"/><path d="M3 21v-2a6 6 0 0 1 12 0v2m2-16a3 3 0 0 1 0 6m4 10v-2a6 6 0 0 0-4-5"/>',
  };
  return `<svg class="icon ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.sun}</svg>`;
};
