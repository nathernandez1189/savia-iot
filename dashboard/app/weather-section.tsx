'use client';
import { useEffect, useRef, useState } from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { ArrowDownUp, ArrowRight, Cloud, CloudFog, CloudLightning, CloudRain, Droplets, ExternalLink, Globe2, Info, LoaderCircle, MapPin, RefreshCw, Search, Snowflake, Sun, Thermometer, Wind, X } from 'lucide-react';
import type { Reading } from '../lib/protocol';
import { comparison, dayKey, futureHours, LOCATION_KEY, LocationSchema, locationLabel, nextRain, WEATHER_TTL, weatherCondition, weatherTime, type Forecast, type Location, type WeatherMetric } from '../lib/weather';
import { weatherClient } from '../lib/weather-client';

type WeatherState = { placeId: number; data: Forecast; fetchedAt: number; cached: boolean };
const metrics: Record<WeatherMetric, { name: string; unit: string; color: string }> = {
  temperature_2m: { name: 'Temperatura', unit: '°C', color: '#b87142' },
  relative_humidity_2m: { name: 'Humedad', unit: '%', color: '#4b8565' },
  precipitation_probability: { name: 'Prob. de lluvia', unit: '%', color: '#548a9b' },
};
const icons = { sun: Sun, cloud: Cloud, rain: CloudRain, storm: CloudLightning, snow: Snowflake, fog: CloudFog };
function ConditionIcon({ code, size = 25 }: { code: number | null; size?: number }) {
  const condition = weatherCondition(code), Icon = icons[condition.icon];
  return <Icon size={size} aria-hidden="true" />;
}
const value = (n: number | null | undefined, decimals = 0) => n == null ? '—' : n.toLocaleString('es-CO', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
const difference = (n: number | null, unit: string) => n == null ? 'No disponible' : `${n > 0 ? '+' : ''}${value(n, 1)} ${unit}`;

export default function WeatherSection({ reading, live, now }: { reading: Reading | null; live: boolean; now: number }) {
  const [location, setLocation] = useState<Location | null>(null);
  const [ready, setReady] = useState(false), [editing, setEditing] = useState(false), [storageNote, setStorageNote] = useState('');
  const [query, setQuery] = useState(''), [results, setResults] = useState<Location[] | null>(null);
  const [searching, setSearching] = useState(false), [searchError, setSearchError] = useState('');
  const [weather, setWeather] = useState<WeatherState | null>(null), [loading, setLoading] = useState(false), [error, setError] = useState('');
  const [revision, setRevision] = useState(0), [metric, setMetric] = useState<WeatherMetric>('temperature_2m'), [selectedDay, setSelectedDay] = useState('');
  const searchRevision = useRef(0), searchInput = useRef<HTMLInputElement>(null);
  useEffect(() => {
    try {
      const saved = localStorage.getItem(LOCATION_KEY);
      if (saved) {
        const parsed = LocationSchema.safeParse(JSON.parse(saved));
        // Hydration reads only a location the user previously chose; there is no default place.
        // eslint-disable-next-line react-hooks/set-state-in-effect
        if (parsed.success) setLocation(parsed.data);
      }
    } catch { setStorageNote('Tu navegador no permite guardar la ubicación. Podrás elegirla para esta sesión.'); }
    setReady(true);
    // This is a request counter, not a DOM ref; invalidating it prevents late search updates.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    return () => { searchRevision.current++; };
  }, []);
  useEffect(() => { if (editing) searchInput.current?.focus(); }, [editing]);
  useEffect(() => {
    if (!location) return;
    let active = true;
    // This component owns only weather state. It never writes to MQTT, device readings or controls.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true); setError('');
    weatherClient.forecast(location).then(result => {
      if (active) setWeather({ ...result, placeId: location.id });
    }).catch(cause => { if (active) setError(cause instanceof Error ? cause.message : 'No pudimos consultar el clima.'); })
      .finally(() => { if (active) setLoading(false); });
    const refresh = () => { if (document.visibilityState === 'visible') setRevision(n => n + 1); };
    const interval = setInterval(refresh, WEATHER_TTL);
    document.addEventListener('visibilitychange', refresh);
    return () => { active = false; clearInterval(interval); document.removeEventListener('visibilitychange', refresh); };
  }, [location, revision]);

  async function search() {
    const request = ++searchRevision.current;
    if (query.trim().length < 3) { setSearchError('Escribe al menos 3 caracteres para buscar.'); return; }
    setSearching(true); setSearchError(''); setResults(null);
    try {
      const response = await weatherClient.search(query);
      if (request === searchRevision.current) setResults(response.data.results ?? []);
    } catch (cause) { if (request === searchRevision.current) setSearchError(cause instanceof Error ? cause.message : 'No pudimos buscar ese lugar.'); }
    finally { if (request === searchRevision.current) setSearching(false); }
  }
  function choose(place: Location | null) {
    searchRevision.current++; setSearching(false); setLocation(place); setWeather(null); setError(''); setLoading(false); setEditing(false); setResults(null); setQuery(''); setSelectedDay(''); setStorageNote('');
    try { if (place) localStorage.setItem(LOCATION_KEY, JSON.stringify(place)); else localStorage.removeItem(LOCATION_KEY); }
    catch { setStorageNote('El cambio se aplicó a esta sesión, pero el navegador no permitió guardarlo.'); }
  }
  const current = location && weather?.placeId === location.id ? weather : null;
  const data = current?.data;
  const oldWeather = !!current && (now - current.fetchedAt >= WEATHER_TTL || now - current.data.current.time * 1000 > 90 * 60_000);
  const rain = data ? nextRain(data, now) : null;
  const compare = current ? comparison(reading, live, current.data, now, current.fetchedAt) : null;
  const hourData = data ? (selectedDay ? futureHours(data, now, selectedDay) : data.hourly.time.flatMap((t, i) => t * 1000 >= now ? [{ time: t * 1000, temperature_2m: data.hourly.temperature_2m[i], relative_humidity_2m: data.hourly.relative_humidity_2m[i], precipitation_probability: data.hourly.precipitation_probability[i] }] : []).slice(0, 24)) : [];
  const metricInfo = metrics[metric];

  return <section className="weather-section" id="clima" aria-labelledby="weather-title">
    <div className="section-heading"><div><div className="eyebrow">UNA MIRADA MÁS ALLÁ DEL INVERNADERO</div><h2 id="weather-title">El clima alrededor de tu cultivo<span>.</span></h2><p>Anticípate al día. Explora el ambiente exterior y lo que viene.</p></div><span className="weather-source-pill"><Globe2 size={14}/>Open-Meteo · Exterior</span></div>
    <div className="weather-shell">
      <div className="weather-location-bar"><div className="weather-location"><span className="weather-map-icon"><MapPin size={22}/></span><div><span className="weather-overline">{location ? 'UBICACIÓN ELEGIDA' : 'UBICACIÓN DEL CULTIVO'}</span><strong>{location ? location.name : '¿Dónde está tu invernadero?'}</strong><p>{location ? `${location.admin1 || 'Región no informada'} · ${location.country || location.country_code || 'País no informado'}` : 'Elige un municipio para consultar su clima exterior.'}</p></div></div>{location && <div className="weather-location-actions"><button className="button secondary" onClick={() => setEditing(!editing)}>{editing ? 'Cerrar búsqueda' : 'Cambiar ubicación'}</button><button className="weather-icon-button" onClick={() => choose(null)} aria-label="Quitar ubicación" title="Quitar ubicación"><X size={17}/></button></div>}</div>
      {!ready ? <div className="weather-status" role="status"><LoaderCircle className="spinning" size={20}/>Preparando tu ubicación…</div> : (!location || editing) && <div className="location-picker">
        <form onSubmit={event => { event.preventDefault(); void search(); }} className="location-form"><label htmlFor="municipality-search">Ciudad o municipio</label><div className="location-search-row"><div className="location-input-wrap"><Search size={18}/><input ref={searchInput} id="municipality-search" type="search" autoComplete="off" placeholder="Escribe el nombre de tu municipio" maxLength={120} value={query} onChange={event => { setQuery(event.target.value); searchRevision.current++; setSearching(false); setResults(null); setSearchError(''); }} aria-describedby="location-search-help"/></div><button className="button lime" disabled={searching || query.trim().length < 3} type="submit">{searching ? <LoaderCircle size={16} className="spinning"/> : <Search size={16}/>}Buscar</button></div><p id="location-search-help">Escribe al menos 3 letras y pulsa Buscar. Revisa la región y el país antes de elegir.</p></form>
        <div aria-live="polite">{searching && <p className="weather-status"><LoaderCircle size={17} className="spinning"/>Buscando municipios…</p>}{searchError && <div className="weather-error" role="alert"><p>{searchError}</p><button className="button secondary" onClick={() => void search()} disabled={searching || query.trim().length < 3}>Reintentar búsqueda</button></div>}{results?.length === 0 && <p className="weather-status"><MapPin size={18}/>No encontramos ese municipio. Prueba otro nombre o añade el país.</p>}</div>
        {!!results?.length && <ul className="location-results" aria-label="Municipios encontrados">{results.map(place => <li key={place.id}><button onClick={() => choose(place)} aria-label={`Elegir ${locationLabel(place)}`}><MapPin size={17}/><span><strong>{place.name}</strong><small>{place.admin1 || 'Región no informada'} · {place.country || place.country_code || 'País no informado'}</small></span><ArrowRight size={17}/></button></li>)}</ul>}
        {!location && !results && !searching && !searchError && <div className="weather-welcome"><span className="weather-welcome-icon"><Sun size={35}/><Cloud size={25}/></span><div><h3>Un contexto exterior para cuidar mejor.</h3><p>Consulta siete días de pronóstico, explora cada hora y compara con tu prototipo. La ubicación se guarda solo en este navegador.</p></div></div>}
        <p className="geocoding-credit">Búsqueda: <a href="https://open-meteo.com/en/docs/geocoding-api" target="_blank" rel="noreferrer">Open-Meteo</a> · Lugares: <a href="https://www.geonames.org/" target="_blank" rel="noreferrer">GeoNames</a>.</p>
      </div>}
      {storageNote && <p className="weather-storage-note" role="status">{storageNote}</p>}
      {location && loading && <div className="weather-status" role="status"><LoaderCircle className="spinning" size={19}/>{data ? 'Comprobando la actualización del clima…' : `Consultando el clima de ${location.name}…`}</div>}
      {location && error && <div className="weather-error" role="alert"><div><strong>No pudimos actualizar el clima exterior.</strong><p>{error}</p><small>El monitoreo de Wokwi y los controles de ventilación funcionan por separado.</small></div><button className="button secondary" onClick={() => setRevision(n => n + 1)} disabled={loading}><RefreshCw size={15}/>Reintentar clima</button></div>}
      {data && current && <div className="weather-content">
        <div className="weather-summary"><div><span className="weather-model-label">ESTIMACIÓN EXTERIOR · MODELO METEOROLÓGICO</span><h3><ConditionIcon code={data.current.weather_code}/>{weatherCondition(data.current.weather_code).label}</h3><p>Dato del {weatherTime(data.current.time * 1000, data.timezone)} · {data.timezone}</p></div><button className="weather-refresh" onClick={() => setRevision(n => n + 1)} disabled={loading}><RefreshCw size={15} className={loading ? 'spinning' : ''}/>{loading ? 'Consultando…' : 'Actualizar clima'}</button></div>
        {oldWeather && <div className="weather-stale" role="status"><Info size={17}/>Datos exteriores pendientes de actualización. Revisa la fecha; la comparación está pausada.</div>}
        <div className="outdoor-metrics"><article><span><Thermometer size={17}/>Temperatura exterior</span><strong>{value(data.current.temperature_2m, 1)}<small>°C</small></strong><p>Estimación a 2 m del suelo</p></article><article><span><Droplets size={17}/>Humedad exterior</span><strong>{value(data.current.relative_humidity_2m)}<small>% HR</small></strong><p>Humedad relativa del aire</p></article><article><span><Wind size={17}/>Viento exterior</span><strong>{value(data.current.wind_speed_10m, 1)}<small>km/h</small></strong><p>Estimación a 10 m del suelo</p></article><article className="rain-metric"><span><CloudRain size={17}/>Probabilidad de lluvia</span><strong>{value(rain?.value)}<small>%</small></strong><p>{rain ? `Pronóstico horario · ${weatherTime(rain.time, data.timezone, false)}` : 'Sin pronóstico para la próxima hora'}</p></article></div>
        <div className="forecast-heading"><div><h3>Tu semana, a primera vista</h3><p>Pronóstico de 7 días, desde hoy. Elige un día para explorar sus próximas horas.</p></div><span className="forecast-badge">PRONÓSTICO</span></div>
        <div className="forecast-days">{data.daily.time.map((seconds, index) => {
          const time = seconds * 1000, key = dayKey(time, data.timezone), condition = weatherCondition(data.daily.weather_code[index]);
          const weekday = new Intl.DateTimeFormat('es-CO', { timeZone: data.timezone, weekday: 'short' }).format(time);
          const date = new Intl.DateTimeFormat('es-CO', { timeZone: data.timezone, day: 'numeric', month: 'short' }).format(time);
          return <button key={seconds} className={`forecast-day ${selectedDay === key ? 'selected' : ''}`} aria-pressed={selectedDay === key} aria-label={`Ver pronóstico del ${date}: ${condition.label}`} onClick={() => setSelectedDay(key)}><strong>{key === dayKey(now, data.timezone) ? 'Hoy' : weekday}</strong><small>{date}</small><ConditionIcon code={data.daily.weather_code[index]} size={28}/><span className="day-condition">{condition.label}</span><span className="day-temperatures">{value(data.daily.temperature_2m_max[index])}° <em>{value(data.daily.temperature_2m_min[index])}°</em></span><span className="day-rain"><Droplets size={12}/>{value(data.daily.precipitation_probability_max[index])}%</span></button>;
        })}</div>
        <p className="forecast-legend">Máxima / mínima en °C · Gota: probabilidad máxima diaria de precipitación.</p>
        <div className="forecast-chart-card"><div className="forecast-chart-heading"><div><h3>Cada hora cuenta</h3><p>{selectedDay ? `Horas futuras del día elegido · ${selectedDay}` : 'Próximas 24 horas disponibles'} · Hora local del municipio</p></div>{selectedDay && <button className="weather-refresh" onClick={() => setSelectedDay('')}>Ver próximas 24 h</button>}</div><div className="forecast-tabs" role="group" aria-label="Variable del pronóstico">{(Object.keys(metrics) as WeatherMetric[]).map(key => <button key={key} aria-pressed={key === metric} className={key === metric ? 'active' : ''} onClick={() => setMetric(key)}>{metrics[key].name}</button>)}</div>
          {hourData.length ? <><div className="forecast-chart" aria-label={`Gráfico de ${metricInfo.name.toLowerCase()} exterior, pronóstico en ${metricInfo.unit}`}><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 300, height: 230 }}><AreaChart data={hourData} margin={{ top: 18, right: 15, left: -15, bottom: 4 }} accessibilityLayer><defs><linearGradient id="weather-area-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={metricInfo.color} stopOpacity={0.2}/><stop offset="100%" stopColor={metricInfo.color} stopOpacity={0.02}/></linearGradient></defs><CartesianGrid stroke="#e7ecdf" vertical={false}/><XAxis dataKey="time" tickFormatter={time => weatherTime(time, data.timezone, false)} minTickGap={45} tick={{ fontSize: 10, fill: '#697b62' }} axisLine={false} tickLine={false}/><YAxis domain={metric === 'temperature_2m' ? ['auto', 'auto'] : [0, 100]} unit={metricInfo.unit} tickFormatter={n => value(Number(n), Number.isInteger(Number(n)) ? 0 : 1)} tick={{ fontSize: 10, fill: '#697b62' }} axisLine={false} tickLine={false}/><Tooltip labelFormatter={time => weatherTime(Number(time), data.timezone)} formatter={n => [n == null ? 'Sin dato' : `${value(Number(n), 1)} ${metricInfo.unit}`, metricInfo.name]} contentStyle={{ borderRadius: 12, borderColor: '#dce5d3', fontSize: 12 }}/><Area type="linear" dataKey={metric} stroke={metricInfo.color} strokeWidth={2.5} fill="url(#weather-area-fill)" connectNulls={false} isAnimationActive={false} activeDot={{ r: 4 }}/></AreaChart></ResponsiveContainer></div><details className="forecast-data-table"><summary>Ver datos horarios en tabla</summary><div className="weather-table-scroll"><table><caption>Pronóstico exterior de Open-Meteo · {data.timezone}</caption><thead><tr><th>Fecha y hora</th><th>Temp. °C</th><th>Humedad %</th><th>Lluvia %</th></tr></thead><tbody>{hourData.map(row => <tr key={row.time}><th scope="row">{weatherTime(row.time, data.timezone)}</th><td>{value(row.temperature_2m, 1)}</td><td>{value(row.relative_humidity_2m)}</td><td>{value(row.precipitation_probability)}</td></tr>)}</tbody></table></div></details></> : <p className="weather-status">No quedan horas futuras disponibles para este día. Elige otro día.</p>}
        </div>
        {compare && <div className="weather-comparison"><div className="comparison-heading"><ArrowDownUp size={20}/><div><h3>Dentro y fuera, con contexto</h3><p>Comparación orientativa: un prototipo simulado y una estimación del exterior.</p></div></div><div className="comparison-sources"><div><span className="source-chip">WOKWI · SIMULACIÓN</span><strong>Última lectura del ESP32 + DHT22</strong><p>{reading ? `${weatherTime(reading.ts, data.timezone)} · ${live && now - reading.ts <= 120_000 && reading.ts <= now + 30_000 ? 'Lectura reciente' : 'Desactualizada'}` : 'Sin lectura del dispositivo'}</p><span>{value(reading?.temperature, 1)} °C <i/> {value(reading?.humidity)} % HR</span></div><div><span className="source-chip exterior">OPEN-METEO · ESTIMACIÓN</span><strong>Ambiente exterior del municipio</strong><p>{weatherTime(data.current.time * 1000, data.timezone)} · {oldWeather ? 'Pendiente de actualizar' : 'Hora del modelo'}</p><span>{value(data.current.temperature_2m, 1)} °C <i/> {value(data.current.relative_humidity_2m)} % HR</span></div></div><div className="comparison-result">{compare.reason ? <p><Info size={16}/>{compare.reason}</p> : <><span>Prototipo − exterior</span><strong>{difference(compare.temperature, '°C')}</strong><strong>{difference(compare.humidity, 'puntos de HR')}</strong></>}</div><p className="comparison-note">Horarios en {data.timezone}. Los horarios no son idénticos. Esto no mide el efecto real del invernadero ni modifica la ventilación. El clima exterior nunca reemplaza una lectura del DHT22.</p></div>}
        <div className="weather-footnote"><Info size={16}/><p>Open-Meteo estima el tiempo exterior con modelos; no es un sensor de tu cultivo. La probabilidad corresponde a precipitación, que puede incluir lluvia o nieve. Las temperaturas y humedades del prototipo siguen viniendo exclusivamente de Wokwi.</p></div>
        <p className="weather-cache-note">Consulta del {weatherTime(current.fetchedAt, data.timezone)} · Respuestas reutilizadas durante 15 minutos. Actualización automática con la página visible. <span>— significa dato no disponible.</span></p>
      </div>}
      <div className="weather-attribution"><span>Datos meteorológicos: <a href="https://open-meteo.com/" target="_blank" rel="noreferrer">Open-Meteo <ExternalLink size={11}/></a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CC BY 4.0</a>. Lugares: <a href="https://www.geonames.org/" target="_blank" rel="noreferrer">GeoNames</a>.</span><span>Integración informativa · Proyecto educativo</span></div>
    </div>
  </section>;
}
