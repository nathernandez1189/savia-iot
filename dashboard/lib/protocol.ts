import { z } from 'zod';
export const TOPIC = 'uao/invernadero/477744536654042113/v2';
export const BROKER = 'wss://broker.emqx.io:8084/mqtt';
export const WOKWI = 'https://wokwi.com/projects/477744536654042113';
export const Measurement = z.object({
  v:z.literal(2), boot:z.string().regex(/^[a-f0-9]{8}$/), seq:z.number().int().positive().max(4294967295),
  up:z.number().int().min(0).max(4294967295), ts:z.number().int().min(0).max(4102444800000),
  temperature:z.number().min(-40).max(80).nullable(), humidity:z.number().min(0).max(100).nullable(),
  mode:z.enum(['AUTO','MANUAL']), fan:z.boolean(), alarm:z.enum(['NORMAL','BAJA','ALTA','SENSOR']),
  reason:z.string().max(60),
}).strict();
export type Reading = z.infer<typeof Measurement>;
export const EventSchema = z.object({id:z.string().min(1).max(100),at:z.number().int().positive().max(4102444800000),kind:z.string().min(1).max(40),detail:z.string().min(1).max(240),level:z.enum(['info','ok','warn'])}).strict();
export type LogEvent = z.infer<typeof EventSchema>;
export const Batch = z.object({readings:z.array(Measurement).max(50).default([]),events:z.array(EventSchema).max(20).default([])}).strict();
export function isFresh(connected:boolean,lastLive:number,now:number) {return connected && lastLive>0 && now-lastLive < 16000;}
export function makeCommand(op:string,r:Reading,id:string) {
  if(!['ON','OFF','AUTO','CUT'].includes(op)) throw new Error('Orden no permitida');
  return {v:2,id,op,boot:r.boot,ref_up:r.up};
}
export function mergeReadings(before:Reading[],incoming:Reading[],limit=6000):Reading[] {
  const m=new Map(before.map(r=>[r.boot+':'+r.seq,r]));
  incoming.forEach(r=>m.set(r.boot+':'+r.seq,r));
  return [...m.values()].sort((a,b)=>a.ts-b.ts || a.seq-b.seq).slice(-limit);
}
// Reconstruct early samples before NTP using the live timestamp and device uptime.
// Reopening the panel must not make those old samples look like new measurements.
export function normalizeTimestamp(r:Reading,anchor:Reading|null,now:number):Reading {
 if(r.ts>0)return r;
 const delta=anchor?.boot===r.boot?anchor.up-r.up:NaN;
 return {...r,ts:anchor&&anchor.ts>0&&delta>=0?Math.max(1,anchor.ts-delta):now};
}
