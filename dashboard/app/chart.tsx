'use client';
import { useState } from 'react';
import { Activity, ArrowUpRight } from 'lucide-react';
import type { Reading } from '../lib/protocol';
const time=(t:number)=>new Date(t).toLocaleTimeString('es-CO',{timeZone:'America/Bogota',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
export default function Chart({data,field,title,color,unit,thresholds}:{data:Reading[],field:'temperature'|'humidity',title:string,color:string,unit:string,thresholds:number[]}){
 const [hover,setHover]=useState<number|null>(null);
 const vals=data.filter(r=>r[field]!==null&&r.ts>0);
 const shown=vals.filter((_,i)=>i%Math.max(1,Math.ceil(vals.length/400))===0||i===vals.length-1);
 const numbers=shown.map(r=>r[field] as number);
 const lo=field==='temperature'?Math.floor(Math.min(20,...numbers)-2):Math.max(0,Math.floor(Math.min(40,...numbers)-5));
 const hi=field==='temperature'?Math.ceil(Math.max(32,...numbers)+2):Math.min(100,Math.ceil(Math.max(90,...numbers)+5));
 const t0=shown[0]?.ts??0,t1=Math.max(shown.at(-1)?.ts??1,t0+1000);
 const x=(t:number)=>48+(t-t0)/(t1-t0)*602,y=(v:number)=>180-(v-lo)/(hi-lo)*145;
 let path='';shown.forEach((r,i)=>{const p=shown[i-1];path+=`${i===0||(p&&(r.ts-p.ts>16000||r.boot!==p.boot))?'M':'L'}${x(r.ts)},${y(r[field]!)} `});
 const active=hover!==null?shown[hover]:undefined;
 return <article className="chart-card"><div className="chart-heading"><div><span className="chart-dot" style={{background:color}}/>{title}</div><span className="chart-latest">{shown.at(-1)?.[field]?.toFixed(1)??'—'} <small>{unit}</small></span></div>{!shown.length?<div className="chart-empty"><Activity size={27}/><p>Tu historia empieza con la primera lectura.</p><small>Inicia la simulación para ver los datos aquí.</small></div>:<svg role="img" aria-label={`Historial de ${title.toLowerCase()}, ${vals.length} mediciones`} viewBox="0 0 680 226" onMouseLeave={()=>setHover(null)} onMouseMove={e=>{const b=e.currentTarget.getBoundingClientRect(),px=(e.clientX-b.left)/b.width*680;let best=0;shown.forEach((r,i)=>{if(Math.abs(x(r.ts)-px)<Math.abs(x(shown[best].ts)-px))best=i});setHover(best)}}><title>{title}</title>{[0,1,2,3].map(i=>{const v=lo+(hi-lo)*i/3;return <g key={i}><line x1="48" x2="650" y1={y(v)} y2={y(v)} stroke="#edf0e9"/><text x="35" y={y(v)+4} textAnchor="end" className="axis-label">{v.toFixed(0)}</text></g>})}{thresholds.map(v=><g key={v}><line x1="48" x2="650" y1={y(v)} y2={y(v)} stroke="#b0bba7" strokeDasharray="4 6"/><text x="650" y={y(v)-5} textAnchor="end" className="threshold-label">{v} {unit}</text></g>)}<path d={path} fill="none" stroke={color} strokeWidth="3" strokeLinejoin="round"/>{shown.length===1&&<circle cx={x(shown[0].ts)} cy={y(shown[0][field]!)} r="4" fill={color}/>}<text x="48" y="215" className="axis-label">{time(t0)}</text><text x="650" y="215" textAnchor="end" className="axis-label">{time(t1)}</text>{active&&<g><line x1={x(active.ts)} x2={x(active.ts)} y1="32" y2="180" stroke={color} strokeDasharray="3 3"/><circle cx={x(active.ts)} cy={y(active[field]!)} r="5" fill={color} stroke="white" strokeWidth="2"/><g transform={`translate(${Math.max(48,Math.min(505,x(active.ts)-72))},0)`}><rect width="146" height="29" rx="8" fill="#193d30"/><text x="73" y="19" textAnchor="middle" fill="white" fontSize="11">{active[field]?.toFixed(1)} {unit} · {time(active.ts)}</text></g></g>}</svg>}<div className="chart-caption"><span>Líneas punteadas: umbrales de referencia</span><ArrowUpRight size={13}/></div></article>
}
export function Sparkline({data,field,color}:{data:Reading[],field:'temperature'|'humidity',color:string}){
 const vals=data.slice(-36).map(r=>r[field]).filter((v):v is number=>v!==null);
 if(vals.length<2)return <span className="spark-placeholder">Esperando tendencia</span>;
 const min=Math.min(...vals)-1,max=Math.max(...vals)+1;
 return <svg className="sparkline" viewBox="0 0 120 38" role="img" aria-label="Tendencia de las últimas lecturas"><path d={vals.map((v,i)=>`${i?'L':'M'}${i/(vals.length-1)*120},${33-(v-min)/(max-min)*28}`).join(' ')} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round"/></svg>
}
