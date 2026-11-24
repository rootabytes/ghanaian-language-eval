/**
 * Claude Sonnet 5 and Claude Haiku 4.5 on the Twi test sets: English to Akuapem Twi.
 *
 * The prompt and request are the ones used for the published outputs: a single user
 * message, no system prompt, no thinking parameter, max_tokens 300, first line of the
 * reply kept. Sonnet 5's answers on akuapem150 were made on 15 Aug 2026 with this same
 * prompt; everything else on 24 Nov 2026.
 *
 * Resumable: sentences already in a system's output file are skipped.
 *
 *   npm install @anthropic-ai/sdk tsx
 *   ANTHROPIC_API_KEY=... npx tsx scripts/run_claude.ts
 */
import fs from 'fs';
import path from 'path';
import Anthropic from '@anthropic-ai/sdk';

const MODELS = ['claude-sonnet-5', 'claude-haiku-4-5'];
const TARGET = 'prompt:Akuapem';
const DATA = 'data/twi';
const OUT_DIR = 'outputs/twi';
const CONCURRENCY = 6;

type Row = { id: string; english: string; reference: string };
type Out = { set: string; id: string; model: string; target: string; candidate: string };

const outPath = (model: string) => path.join(OUT_DIR, `${model}__prompt_Akuapem.jsonl`);
const readJsonl = <T>(p: string): T[] =>
  fs.existsSync(p) ? fs.readFileSync(p, 'utf-8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l)) : [];

async function main() {
  const client = new Anthropic();
  const sets = fs.readdirSync(DATA).filter((f) => f.endsWith('.jsonl'))
    .map((f) => ({ name: f.replace(/\.jsonl$/, ''), rows: readJsonl<Row>(path.join(DATA, f)) }));

  const todo: { model: string; set: string; row: Row }[] = [];
  for (const model of MODELS) {
    const done = new Set(readJsonl<Out>(outPath(model)).map((r) => `${r.set}|${r.id}`));
    for (const s of sets) for (const row of s.rows) if (!done.has(`${s.name}|${row.id}`)) todo.push({ model, set: s.name, row });
  }
  console.log(`${todo.length} calls to make`);

  let next = 0, ok = 0, failed = 0;
  await Promise.all(Array.from({ length: CONCURRENCY }, async () => {
    while (next < todo.length) {
      const { model, set, row } = todo[next++];
      try {
        const r = await client.messages.create({
          model, max_tokens: 300,
          messages: [{ role: 'user', content:
            `Translate this English sentence into Akuapem Twi. Reply with ONLY the Twi sentence, nothing else.\n\n${row.english}` }],
        });
        if (r.stop_reason === 'refusal') throw new Error('refusal');
        const text = r.content.filter((b): b is Anthropic.TextBlock => b.type === 'text').map((b) => b.text).join('');
        const out: Out = { set, id: row.id, model, target: TARGET, candidate: text.trim().split('\n')[0].trim() };
        fs.appendFileSync(outPath(model), JSON.stringify(out) + '\n');
        if (++ok % 100 === 0) console.log(`  ${ok} done`);
      } catch (e: any) {
        failed++;
        console.error(`  ${model} ${set} ${row.id}: ${e?.status ?? ''} ${e?.message ?? e}`);
        if (e instanceof Anthropic.AuthenticationError) process.exit(1);
      }
    }
  }));
  console.log(`done: ${ok} ok, ${failed} failed. Re-sort and score with: python scripts/score.py twi`);
}

main().catch((e) => { console.error(e); process.exit(1); });
