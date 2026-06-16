# Distillation method — how a large dataset becomes a representative test set

This is the detail behind `scripts/distill.py`. Read it to choose a field mapping, tune
the run, or do the distillation by hand if you can't run the script.

## The core idea

A large dataset of past interactions is not a test set. It is full of three different kinds
of redundancy, and each must be handled differently:

| Regime | What it is | What to do |
|---|---|---|
| **A. Exact / trivial duplicates** | The same input repeated verbatim (`"Add Options"` ×4, `"系统错误"` ×N). | Keep one. |
| **B. Paraphrases (same scenario)** | Different wording, **same intent + same substantive answer** (`"List my open orders"` ≈ `"Could you list all my open orders?"`). | Collapse to one canonical case per cluster. |
| **C. Boilerplate convergence (different scenarios)** | Many **unrelated** asks that all map to one generic answer — a ticket-submission fallback, an out-of-scope refusal, a greeting. | Do **not** collapse by answer (these are distinct intents). Instead **down-sample** to a small fixed quota so they don't flood the suite. |

The trap: if you dedupe by the expected answer alone, you wrongly merge regime C (distinct
intents that share a fallback answer). So dedupe regime A+B on the **input** text, and treat
large same-answer clusters as regime C to be quota-capped, not merged.

## What "the same scenario" means

Two cases are the same scenario when they share **intent** (best proxy: a substantive
expected answer, plus a category/route label) regardless of surface wording. They are
**distinct** despite sharing an answer when that answer is boilerplate (fallback / greeting /
out-of-scope) — then the *inputs* define separate scenarios.

## The selection strategy (why it is failure-weighted)

After dedup you still have far more than 50 unique scenarios, so selection is a stratified
sample, not "take the top N":

1. **Failures first.** SME/known-fail cases are the minority but the highest signal — they
   are scenarios the agent already gets wrong. Reserve ~45% of the budget for them
   (`--fail-weight`), spread across labels and languages.
2. **Pass coverage by label.** Fill the rest with one representative ("medoid": the
   longest, most-specific case) per distinct label/route, proportional to how common that
   label is.
3. **Boilerplate quota.** Cap fallback/greeting/out-of-scope at a few representatives
   (`--boilerplate-quota`, default 4) — enough to test those paths without flooding.
4. **Language quota.** If the data is multilingual, `--min-minority-ratio 0.3` keeps the
   minority language (e.g. non-English) at roughly its real share so coverage isn't lost.

## Field mapping

The script needs to know which columns carry signal:

| Flag | Meaning | Default |
|---|---|---|
| `--input-field` | the user utterance / scenario seed | `input_str` |
| `--expected-field` | the correct answer / expected behavior (list or string) | `expected_behaviors` |
| `--label-field` | the intent / route / category to stratify by | `next_agent_status` |
| `--pass-fail-field` | a field whose value starts with `Pass` or `Fail` | `sme_result` |
| `--parse-coval-description` | parse `key=value \| key=value` labels out of a Coval `description` | off |

If your data has no pass/fail label, the run still works — every case is treated as
"unknown" and selection falls back to label + language coverage (no failure weighting).
If you have no useful label field, pass `--label-field` pointing at any categorical column;
with none, everything lands in one bucket and you still get exact+paraphrase dedup +
boilerplate capping.

## Clustering: heuristic vs embeddings

- **Default (no setup):** character 3-gram **Jaccard** similarity, `--jaccard-threshold 0.5`.
  Works offline, no dependencies, good for catching near-duplicate wording.
- **Better for multilingual / semantic paraphrase:** set `OPENAI_API_KEY` and add
  `--embeddings on` (uses `text-embedding-3-large`, `--embed-threshold 0.85`). Falls back to
  the heuristic automatically on any error.

## Tuning cheatsheet

- Suite feels noisy with fallbacks/greetings → lower `--boilerplate-quota`.
- Not enough coverage of known misses → raise `--fail-weight` (e.g. 0.6) or `--target-size`.
- Over-merging distinct cases → raise the threshold (`0.6` Jaccard / `0.9` cosine).
- Under-merging near-dups → lower the threshold.
- Losing a language → set `--min-minority-ratio` to its real share.

## Doing it by hand (no Python)

If you can't run the script, the agent can reproduce the method manually on a few hundred
rows: (1) drop rows whose expected answer is empty or "n/a"; (2) group by your label field;
(3) within each label, drop verbatim-duplicate inputs and merge obvious paraphrases, keeping
the most specific one; (4) set aside the big "everything → submit a ticket / out of scope /
hello" groups and keep just 1–2 of each; (5) pick your final 20–40: start with every known
failure, then add one clear example per remaining label, then a couple of boilerplate
representatives, keeping the language mix. Write them as NDJSON
(`{"input_str","expected_output_str","description"}`) and load with
`coval test-cases create --test-set-id <ID> --stdin`.

## Output contract

`distilled.ndjson` is one JSON object per line, ready for `--stdin`:
```json
{"input_str": "...", "expected_output_str": "...", "description": "distilled from <source> | journey=... | sme_result=..."}
```
The `description` carries provenance + the parsed labels so each distilled case is traceable
back to its origin.
