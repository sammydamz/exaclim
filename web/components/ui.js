import '@ui-sdk/web/button';
import '@ui-sdk/web/tabs';
import '@ui-sdk/web/field';
import '@ui-sdk/web/number-input';
import '@ui-sdk/web/select';
import '@ui-sdk/web/checkbox';
import '@ui-sdk/web/switch';
import '@ui-sdk/web/meter';
import '@ui-sdk/web/alert-dialog';
import { createAgent } from '@ui-sdk/web/agent';

export const agent = createAgent();

export function onAction(selector, callback) {
  const button = document.querySelector(selector).closest('ui-button');
  button.addEventListener('action', event => {
    event.detail.waitUntil(Promise.resolve(callback(event)));
  });
}

export function setValue(key, value) {
  const field = document.querySelector(`#field-${key}`);
  if (typeof value === 'boolean') field.api.setChecked(value);
  else field.api.setValue(value);
}

export function getValue(key) {
  const field = document.querySelector(`#field-${key}`);
  return typeof field.api.getChecked === 'function' ? field.api.getChecked() : field.api.getValue();
}
