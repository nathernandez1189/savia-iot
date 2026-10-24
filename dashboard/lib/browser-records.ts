import { Measurement, EventSchema, type Reading, type LogEvent } from './protocol';
let connection:Promise<IDBDatabase>|undefined;
function db(){
 if(!connection)connection=new Promise<IDBDatabase>((resolve,reject)=>{
  const req=indexedDB.open('savia-iot-history-v1',1);
  req.onupgradeneeded=()=>{const d=req.result;const r=d.createObjectStore('readings',{keyPath:['boot','seq']});r.createIndex('ts','ts');const e=d.createObjectStore('events',{keyPath:'id'});e.createIndex('at','at');};
  req.onsuccess=()=>{req.result.onversionchange=()=>{req.result.close();connection=undefined;};resolve(req.result);};
  req.onerror=()=>{connection=undefined;reject(req.error);};
  req.onblocked=()=>{connection=undefined;reject(new Error('Cierra otras pestañas de Savia IoT para actualizar el historial.'));};
 });
 return connection;
}
function done(tx:IDBTransaction){return new Promise<void>((resolve,reject)=>{tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error??new Error('Guardado interrumpido.'));});}
export async function saveRecords(readings:Reading[],events:LogEvent[]){
 const validReadings=readings.map(r=>Measurement.parse(r));const validEvents=events.map(e=>EventSchema.parse(e));
 const d=await db();const tx=d.transaction(['readings','events'],'readwrite');const finished=done(tx);
 for(const r of validReadings)tx.objectStore('readings').put(r);
 for(const e of validEvents)tx.objectStore('events').put(e);
 await finished;
}
function recent<T>(store:IDBObjectStore,index:string,cutoff:number,limit:number){return new Promise<T[]>((resolve,reject)=>{
 const rows:T[]=[];const req=store.index(index).openCursor(IDBKeyRange.lowerBound(cutoff),'prev');
 req.onsuccess=()=>{const c=req.result;if(!c||rows.length>=limit){resolve(rows);return;}rows.push(c.value as T);c.continue();};req.onerror=()=>reject(req.error);
});}
export async function readRecords(hours:number){
 const d=await db();const tx=d.transaction(['readings','events'],'readonly');const finished=done(tx);
 const rs=tx.objectStore('readings');const es=tx.objectStore('events');
 const count=new Promise<number>((resolve,reject)=>{const r=rs.count();r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
 const [readings,events,total]=await Promise.all([recent<Reading>(rs,'ts',Date.now()-hours*3600000,6000),recent<LogEvent>(es,'at',0,80),count]);
 await finished;return {readings:readings.reverse(),events,total};
}
