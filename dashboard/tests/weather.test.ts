import assert from 'node:assert/strict';
import test from 'node:test';
import { comparison, dayKey, ForecastSchema, futureHours, LocationSchema, locationLabel, nextRain, WEATHER_TTL, type Forecast } from '../lib/weather.ts';
import { createWeatherClient } from '../lib/weather-client.ts';

// Synthetic fixtures belong to tests only; the interface never receives them.
const now = Date.UTC(2026, 9, 13, 20, 15);
const place = { id: 1, name: 'Lugar de prueba', latitude: 6.25, longitude: -75.56, admin1: 'Región', country: 'País', timezone: 'America/Bogota' };
const data: Forecast = {
  timezone: 'America/Bogota',
  current: { time: now / 1000 - 300, temperature_2m: 24, relative_humidity_2m: 80, wind_speed_10m: 8, weather_code: 3 },
  current_units: { time: 'unixtime', temperature_2m: '°C', relative_humidity_2m: '%', wind_speed_10m: 'km/h' },
  hourly_units: { time: 'unixtime', temperature_2m: '°C', relative_humidity_2m: '%', precipitation_probability: '%' },
  daily_units: { time: 'unixtime', temperature_2m_max: '°C', temperature_2m_min: '°C', precipitation_probability_max: '%' },
  hourly: { time: [now / 1000 - 900, now / 1000 + 2700, now / 1000 + 6300], temperature_2m: [24, null, 26], relative_humidity_2m: [80, 81, 82], precipitation_probability: [10, 20, null] },
  daily: { time: [Date.UTC(2026, 9, 13, 5) / 1000], weather_code: [3], temperature_2m_max: [27], temperature_2m_min: [17], precipitation_probability_max: [70] },
};
const sample = { v: 2 as const, boot: 'abcdef01', seq: 1, up: 10000, ts: now - 5000, temperature: 29, humidity: 65, mode: 'AUTO' as const, fan: false, alarm: 'NORMAL' as const, reason: 'lectura' };
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

test('validates arrays, units, ranges and timezone without inventing missing readings', () => {
  assert.equal(ForecastSchema.safeParse(data).success, true);
  assert.equal(ForecastSchema.safeParse({ ...data, hourly: { ...data.hourly, temperature_2m: [24] } }).success, false);
  assert.equal(ForecastSchema.safeParse({ ...data, current_units: { ...data.current_units, wind_speed_10m: 'mph' } }).success, false);
  assert.equal(ForecastSchema.safeParse({ ...data, timezone: 'made/up' }).success, false);
  assert.equal(ForecastSchema.safeParse({ ...data, current: { ...data.current, relative_humidity_2m: 102 } }).success, false);
  assert.equal(LocationSchema.safeParse({ ...place, latitude: 200 }).success, false);
  assert.equal(locationLabel(place), 'Lugar de prueba · Región · País');
});
test('timestamps use the chosen timezone; only future hours and actual rain probabilities are shown', () => {
  assert.equal(dayKey(Date.UTC(2026, 9, 14, 2), 'America/Bogota'), '2026-10-13');
  const hours = futureHours(data, now, '2026-10-13');
  assert.equal(hours.length, 2); assert.equal(hours[0].temperature_2m, null);
  assert.deepEqual(nextRain(data, now), { time: now + 2700000, value: 20 });
  assert.equal(nextRain(data, now + 7_200_000), null);
});
test('comparison blocks stale, disconnected, future and missing telemetry and preserves null fields', () => {
  assert.equal(comparison(sample, true, data, now, now).temperature, 5);
  assert.equal(comparison(sample, true, data, now, now).humidity, -15);
  for (const reading of [null, { ...sample, ts: now - 121000 }, { ...sample, ts: now + 60000 }])
    assert.equal(comparison(reading, true, data, now, now).temperature, null);
  assert.equal(comparison(sample, false, data, now, now).temperature, null);
  assert.equal(comparison(sample, true, data, now, now - WEATHER_TTL - 1).temperature, null);
  assert.equal(comparison(sample, true, { ...data, current: { ...data.current, time: now / 1000 - 5500 } }, now, now).temperature, null);
  const result = comparison({ ...sample, temperature: null }, true, data, now, now);
  assert.equal(result.temperature, null); assert.equal(result.humidity, -15);
});
test('deduplicates concurrent requests, caches across clients, expires and separates locations', async () => {
  let time = now, calls = 0, store = '';
  const storage = () => ({ getItem: () => store, setItem: (_key: string, value: string) => { store = value; } });
  const fetcher: typeof fetch = async () => { calls++; return response(data); };
  const client = createWeatherClient({ fetcher, clock: () => time, storage });
  await Promise.all([client.forecast(place), client.forecast(place)]);
  assert.equal(calls, 1);
  assert.equal((await client.forecast(place)).cached, true);
  const reopened = createWeatherClient({ fetcher, clock: () => time, storage });
  assert.equal((await reopened.forecast(place)).cached, true); assert.equal(calls, 1);
  await client.forecast({ ...place, id: 2, latitude: 8 }); assert.equal(calls, 2);
  time += WEATHER_TTL;
  await client.forecast(place); assert.equal(calls, 3);
});
test('search rejects too-short input locally and caches empty results', async () => {
  let calls = 0;
  const client = createWeatherClient({ fetcher: async () => { calls++; return response({}); } });
  await assert.rejects(client.search('ab'), /3 caracteres/); assert.equal(calls, 0);
  assert.equal((await client.search('ZZZ')).data.results, undefined);
  assert.equal((await client.search(' zzz ')).cached, true); assert.equal(calls, 1);
});
test('network errors have retry cooldowns and never return fake or expired data', async () => {
  let time = now, failed = false, calls = 0;
  const client = createWeatherClient({ clock: () => time, fetcher: async () => { calls++; if (failed) throw Error('offline'); return response(data); } });
  await client.forecast(place); failed = true; time += WEATHER_TTL;
  await assert.rejects(client.forecast(place), /conectar/);
  await assert.rejects(client.forecast(place), /Espera un minuto/); assert.equal(calls, 2);
  time += 60000; failed = false;
  assert.equal((await client.forecast(place)).cached, false); assert.equal(calls, 3);
});
test('handles rate limits, malformed responses, unavailable storage and timeouts', async () => {
  const limited = createWeatherClient({ fetcher: async () => response({}, 429) });
  await assert.rejects(limited.forecast(place), /límite temporal/);
  await assert.rejects(limited.search('Madrid'), /Espera un minuto/);
  const invalid = createWeatherClient({ fetcher: async () => response({ current: { temperature_2m: 'invented' } }) });
  await assert.rejects(invalid.forecast(place), /incompleta/);
  const blockedStorage = createWeatherClient({ fetcher: async () => response(data), storage: () => { throw Error('denied'); } });
  assert.equal((await blockedStorage.forecast(place)).data.current.temperature_2m, 24);
  const slow = createWeatherClient({ timeoutMs: 10, fetcher: async (_url, init) => new Promise((_resolve, reject) => { init?.signal?.addEventListener('abort', () => reject(Error('aborted')), { once: true }); }) });
  await assert.rejects(slow.forecast(place), /tardó demasiado/);
});
