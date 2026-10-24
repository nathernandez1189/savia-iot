import assert from 'node:assert/strict';
import test from 'node:test';
import { Measurement, Batch, isFresh, makeCommand, mergeReadings, normalizeTimestamp } from '../lib/protocol.ts';
const sample={v:2 as const,boot:'abcdef01',seq:1,up:1000,ts:1791870000000,temperature:31,humidity:65,mode:'AUTO' as const,fan:true,alarm:'NORMAL' as const,reason:'lectura'};
test('rejects malformed sensor data and oversized ingestion',()=>{
 assert.equal(Measurement.safeParse({...sample,humidity:140}).success,false);
 assert.equal(Measurement.safeParse({...sample,fan:'false'}).success,false);
 assert.equal(Batch.safeParse({readings:Array(51).fill(sample)}).success,false);
 assert.equal(Measurement.safeParse({...sample,temperature:null,humidity:null,alarm:'SENSOR'}).success,true);
});
test('stale or disconnected devices cannot receive UI commands',()=>{
 assert.equal(isFresh(true,1000,16999),true);assert.equal(isFresh(true,1000,17000),false);
 assert.equal(isFresh(false,1000,1001),false);assert.equal(isFresh(true,0,1001),false);
});
test('commands bind to a device session and freshness reference',()=>{
 assert.deepEqual(makeCommand('OFF',sample,'x'),{v:2,id:'x',op:'OFF',boot:'abcdef01',ref_up:1000});
 assert.throws(()=>makeCommand('DELETE',sample,'x'));
});
test('history backfill deduplicates and orders before keeping newest records',()=>{
 const second={...sample,seq:2,ts:sample.ts+5000};
 assert.deepEqual(mergeReadings([second],[sample,second]),[sample,second]);
 assert.deepEqual(mergeReadings([sample],[second],1),[second]);
});
test('early backfill keeps its original position in time on subsequent reloads',()=>{
 const anchor={...sample,seq:5,up:21000,ts:sample.ts+20000};
 const early={...sample,ts:0};
 assert.equal(normalizeTimestamp(early,anchor,anchor.ts+90000).ts,sample.ts);
 assert.equal(normalizeTimestamp(early,anchor,anchor.ts+190000).ts,sample.ts);
 assert.equal(normalizeTimestamp(sample,anchor,999).ts,sample.ts);
});
