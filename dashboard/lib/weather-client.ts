import { z } from 'zod';
import { ForecastSchema, GeocodingSchema, GEOCODING_TTL, WEATHER_TTL, geocodingUrl, forecastUrl, type Location } from './weather.ts';

type CacheEntry = { data: unknown; fetchedAt: number };
type StoragePort = Pick<Storage, 'getItem' | 'setItem'>;
export class WeatherRequestError extends Error {}

// Bounded cache and in-flight deduplication also cover quick location changes and React remounts.
export function createWeatherClient(options: { fetcher?: typeof fetch; clock?: () => number; storage?: () => StoragePort | undefined; timeoutMs?: number } = {}) {
  const fetcher = options.fetcher ?? fetch, clock = options.clock ?? Date.now;
  const entries = new Map<string, CacheEntry>();
  const pending = new Map<string, Promise<CacheEntry>>();
  const cooldowns = new Map<string, number>();
  let loaded = false;
  let rateLimitUntil = 0;
  function load() {
    if (loaded) return; loaded = true;
    try {
      const raw = JSON.parse(options.storage?.()?.getItem('savia:weather-cache:v1') || '[]');
      const parsed = z.array(z.tuple([z.string(), z.object({ data: z.unknown(), fetchedAt: z.number() })])).max(20).safeParse(raw);
      if (parsed.success) for (const [key, value] of parsed.data) entries.set(key, { data: value.data, fetchedAt: value.fetchedAt });
    } catch { /* Storage unavailable: the in-memory cache remains usable. */ }
  }
  function save() {
    while (entries.size > 20) entries.delete(entries.keys().next().value!);
    try { options.storage?.()?.setItem('savia:weather-cache:v1', JSON.stringify([...entries])); } catch { /* No dependency on storage permission. */ }
  }
  async function request<T>(url: string, ttl: number, schema: z.ZodType<T>): Promise<{ data: T; fetchedAt: number; cached: boolean }> {
    load();
    const old = entries.get(url);
    if (old && clock() >= old.fetchedAt && clock() - old.fetchedAt < ttl) {
      const parsed = schema.safeParse(old.data);
      if (parsed.success) return { data: parsed.data, fetchedAt: old.fetchedAt, cached: true };
      entries.delete(url);
    }
    let promise = pending.get(url);
    if (!promise) {
      if (clock() < Math.max(cooldowns.get(url) ?? 0, rateLimitUntil)) throw new WeatherRequestError('Espera un minuto antes de volver a intentar. Así evitamos consultas repetidas.');
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), options.timeoutMs ?? 12_000);
      promise = (async () => {
        try {
          const response = await fetcher(url, { signal: controller.signal });
          if (response.status === 429) {
            const retrySeconds = Number(response.headers.get('Retry-After'));
            rateLimitUntil = clock() + Math.max(60_000, Number.isFinite(retrySeconds) ? retrySeconds * 1000 : 0);
            throw new WeatherRequestError('Open-Meteo alcanzó su límite temporal. Espera un minuto y reintenta.');
          }
          if (!response.ok) throw new WeatherRequestError('Open-Meteo no está disponible en este momento. Puedes reintentar.');
          const result = schema.safeParse(await response.json());
          if (!result.success) throw new WeatherRequestError('La respuesta meteorológica está incompleta. Reintenta en unos minutos.');
          const entry = { data: result.data, fetchedAt: clock() };
          entries.delete(url); entries.set(url, entry); save(); cooldowns.delete(url);
          return entry;
        } catch (error) {
          cooldowns.set(url, clock() + 60_000);
          if (cooldowns.size > 30) cooldowns.delete(cooldowns.keys().next().value!);
          if (error instanceof WeatherRequestError) throw error;
          throw new WeatherRequestError(controller.signal.aborted ? 'La consulta tardó demasiado. Comprueba tu conexión y reintenta.' : 'No pudimos conectar con Open-Meteo. Comprueba tu conexión y reintenta.');
        } finally { clearTimeout(timer); pending.delete(url); }
      })();
      pending.set(url, promise);
    }
    const entry = await promise;
    return { data: schema.parse(entry.data), fetchedAt: entry.fetchedAt, cached: false };
  }
  return {
    search: (query: string) => {
      if (query.trim().length < 3) return Promise.reject(new WeatherRequestError('Escribe al menos 3 caracteres para buscar.'));
      return request(geocodingUrl(query.trim().toLocaleLowerCase('es')), GEOCODING_TTL, GeocodingSchema);
    },
    forecast: (place: Location) => request(forecastUrl(place), WEATHER_TTL, ForecastSchema),
  };
}
export const weatherClient = createWeatherClient({ storage: () => typeof window === 'undefined' ? undefined : window.sessionStorage });
