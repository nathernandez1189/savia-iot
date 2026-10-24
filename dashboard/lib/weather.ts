import { z } from 'zod';
import type { Reading } from './protocol';

export const WEATHER_TTL = 15 * 60_000;
export const GEOCODING_TTL = 24 * 60 * 60_000;
export const LOCATION_KEY = 'savia:location:v1';
const timezone = z.string().refine(value => {
  try { new Intl.DateTimeFormat('es', { timeZone: value }); return true; } catch { return false; }
});
export const LocationSchema = z.object({
  id: z.number().int(), name: z.string().min(1).max(200),
  latitude: z.number().min(-90).max(90), longitude: z.number().min(-180).max(180),
  admin1: z.string().optional(), country: z.string().optional(),
  country_code: z.string().optional(), timezone: timezone.optional(),
});
export type Location = z.infer<typeof LocationSchema>;
export const GeocodingSchema = z.object({ results: z.array(LocationSchema).max(20).optional() });
const temperature = z.number().min(-100).max(70).nullable();
const percent = z.number().min(0).max(100).nullable();
const code = z.number().int().min(0).max(99).nullable();
const times = z.array(z.number().int().positive()).min(1).max(200);
export const ForecastSchema = z.object({
  timezone,
  current: z.object({ time: z.number().positive(), temperature_2m: temperature,
    relative_humidity_2m: percent, wind_speed_10m: z.number().min(0).max(500).nullable(), weather_code: code }),
  current_units: z.object({ time: z.literal('unixtime'), temperature_2m: z.literal('°C'), relative_humidity_2m: z.literal('%'), wind_speed_10m: z.literal('km/h') }),
  hourly_units: z.object({ time: z.literal('unixtime'), temperature_2m: z.literal('°C'), relative_humidity_2m: z.literal('%'), precipitation_probability: z.literal('%') }),
  daily_units: z.object({ time: z.literal('unixtime'), temperature_2m_max: z.literal('°C'), temperature_2m_min: z.literal('°C'), precipitation_probability_max: z.literal('%') }),
  hourly: z.object({ time: times, temperature_2m: z.array(temperature), relative_humidity_2m: z.array(percent), precipitation_probability: z.array(percent) }),
  daily: z.object({ time: times.max(7), weather_code: z.array(code), temperature_2m_max: z.array(temperature), temperature_2m_min: z.array(temperature), precipitation_probability_max: z.array(percent) }),
}).superRefine((data, context) => {
  for (const group of [data.hourly, data.daily]) {
    if (Object.values(group).some(values => values.length !== group.time.length) ||
      group.time.some((value, index) => index > 0 && value <= group.time[index - 1])) {
      context.addIssue({ code: z.ZodIssueCode.custom, message: 'Serie meteorológica incompleta o desordenada.' });
    }
  }
});
export type Forecast = z.infer<typeof ForecastSchema>;
export type WeatherMetric = 'temperature_2m' | 'relative_humidity_2m' | 'precipitation_probability';

export function locationLabel(place: Location) {
  return `${place.name} · ${place.admin1 || 'Región no informada'} · ${place.country || place.country_code || 'País no informado'}`;
}
export function geocodingUrl(query: string) {
  const params = new URLSearchParams({ name: query.trim(), count: '8', language: 'es', format: 'json' });
  return `https://geocoding-api.open-meteo.com/v1/search?${params}`;
}
export function forecastUrl(place: Location) {
  const params = new URLSearchParams({ latitude: String(place.latitude), longitude: String(place.longitude),
    current: 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
    hourly: 'temperature_2m,relative_humidity_2m,precipitation_probability',
    daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max',
    forecast_days: '7', timezone: 'auto', timeformat: 'unixtime', temperature_unit: 'celsius', wind_speed_unit: 'kmh' });
  return `https://api.open-meteo.com/v1/forecast?${params}`;
}
export function weatherTime(ms: number, zone: string, date = true) {
  return new Intl.DateTimeFormat('es-CO', { timeZone: zone,
    ...(date ? { day: '2-digit', month: 'short' } as const : {}), hour: '2-digit', minute: '2-digit', hour12: false }).format(ms);
}
export function dayKey(ms: number, zone: string) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: zone, year: 'numeric', month: '2-digit', day: '2-digit' }).format(ms);
}
export function futureHours(data: Forecast, now: number, selectedDay: string) {
  return data.hourly.time.flatMap((seconds, i) => seconds * 1000 >= now && dayKey(seconds * 1000, data.timezone) === selectedDay
    ? [{ time: seconds * 1000, temperature_2m: data.hourly.temperature_2m[i], relative_humidity_2m: data.hourly.relative_humidity_2m[i], precipitation_probability: data.hourly.precipitation_probability[i] }]
    : []);
}
export function nextRain(data: Forecast, now: number) {
  const i = data.hourly.time.findIndex(t => t * 1000 >= now);
  if (i < 0 || data.hourly.time[i] * 1000 - now > 3_600_000) return null;
  return { time: data.hourly.time[i] * 1000, value: data.hourly.precipitation_probability[i] };
}
// Fresh delivery alone is insufficient: retained/replayed or old device clocks cannot produce a comparison.
export function comparison(reading: Reading | null, live: boolean, data: Forecast, now: number, fetchedAt: number) {
  if (!reading) return { reason: 'Aún no hay una lectura de Wokwi. No se calcula una diferencia.', temperature: null, humidity: null };
  if (!live || reading.ts <= 0 || now - reading.ts > 120_000 || reading.ts - now > 30_000)
    return { reason: 'La lectura de Wokwi está desactualizada. Esperamos una nueva para comparar.', temperature: null, humidity: null };
  const modelAge = now - data.current.time * 1000;
  if (modelAge > 90 * 60_000 || modelAge < -15 * 60_000 || now - fetchedAt > WEATHER_TTL || fetchedAt > now + 30_000)
    return { reason: 'La estimación exterior necesita actualizarse. No se calcula una diferencia.', temperature: null, humidity: null };
  return { reason: '',
    temperature: reading.temperature == null || data.current.temperature_2m == null ? null : reading.temperature - data.current.temperature_2m,
    humidity: reading.humidity == null || data.current.relative_humidity_2m == null ? null : reading.humidity - data.current.relative_humidity_2m };
}
export function weatherCondition(value: number | null): { label: string; icon: 'sun' | 'cloud' | 'rain' | 'storm' | 'snow' | 'fog' } {
  if (value == null) return { label: 'Sin descripción', icon: 'cloud' };
  if (value === 0) return { label: 'Despejado', icon: 'sun' };
  if (value <= 3) return { label: value === 3 ? 'Nublado' : 'Parcialmente nublado', icon: 'cloud' };
  if (value === 45 || value === 48) return { label: 'Niebla', icon: 'fog' };
  if (value >= 95) return { label: 'Tormentas', icon: 'storm' };
  if ([71, 73, 75, 77, 85, 86].includes(value)) return { label: 'Nieve', icon: 'snow' };
  if ([51, 53, 55, 56, 57].includes(value)) return { label: 'Llovizna', icon: 'rain' };
  if ([61, 63, 65, 66, 67, 80, 81, 82].includes(value)) return { label: 'Lluvia', icon: 'rain' };
  return { label: 'Sin descripción', icon: 'cloud' };
}
