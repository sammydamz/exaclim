// Score the current temperature policy and candidate heat-index policy independently.
import {readFileSync} from 'node:fs';
import {weatherHeatIndex, heatBand} from './heat-index.ts';

const lines = readFileSync(process.argv[2], 'utf8').trim().split(/\r?\n/).slice(1);
for (const policy of ['temperature','heat-index']) for (const lead of [1, 2]) {
  let pairs=0, error=0, hits=0, misses=0, falseAlarms=0;
  for (const line of lines) {
    const [day,obsT,obsH,fcT,fcH]=line.split(',').slice(1).map(Number);
    if (day!==lead) continue;
    const observed=weatherHeatIndex(obsT,obsH), predicted=weatherHeatIndex(fcT,fcH);
    if (observed===null || predicted===null) continue;
    pairs++;
    error+=policy==='temperature'?Math.abs(obsT-fcT):Math.abs(observed-predicted);
    const actual=policy==='temperature'?obsT>=32:heatBand(observed)==='red';
    const warning=policy==='temperature'?fcT>=32:heatBand(predicted)==='red';
    if (actual && warning) hits++;
    if (actual && !warning) misses++;
    if (!actual && warning) falseAlarms++;
  }
  if (!pairs) throw new Error('No matched observations for lead '+lead);
  console.log({policy,lead,pairs,MAE_C:+(error/pairs).toFixed(2),hits,misses,falseAlarms});
}
