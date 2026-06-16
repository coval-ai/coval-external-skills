#!/usr/bin/env python3
"""distill.py — turn a large dataset of agent test cases into a small, deduplicated,
representative Coval test set.

Reads cases from a local file (NDJSON / JSON / CSV) or directly from an existing Coval
test set, then:
  1. drops low-information rows (no checkable expected answer),
  2. removes exact + paraphrase duplicates (same scenario, different wording),
  3. down-samples boilerplate-convergence clusters (different scenarios that all map to
     one generic answer, e.g. a fallback / greeting) to a small quota,
  4. selects a stratified, FAILURE-WEIGHTED representative subset across your labels and
     languages up to a target size.

It emits NDJSON ready to bulk-load with the uncapped CLI path:
    coval test-cases create --test-set-id <ID> --stdin

No third-party packages are required (Python 3.9+ stdlib only). Paraphrase clustering
uses a character n-gram Jaccard heuristic by default. If you pass --embeddings on and set
OPENAI_API_KEY, it uses OpenAI embeddings (better for multilingual data); on any failure
it falls back to the heuristic automatically.

Examples
--------
# From an existing (oversized) Coval test set, parsing Coval's pipe-delimited description:
  export COVAL_API_KEY=...
  python distill.py --source coval:jaWW7zpn --parse-coval-description \
    --label-field next_agent_status --pass-fail-field sme_result \
    --target-size 30 --out distilled.ndjson

# From a local CSV with your own columns:
  python distill.py --source cases.csv --input-field question --expected-field answer \
    --label-field intent --target-size 25 --out distilled.ndjson
"""

import argparse
import csv
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

COVAL_API_BASE = os.environ.get("COVAL_API_URL", "https://api.coval.dev").rstrip("/")
NA_PATTERN = re.compile(r"^\s*n/?a\b", re.IGNORECASE)
CJK_PATTERN = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯]")
WORD_PATTERN = re.compile(r"[^\w\s]", re.UNICODE)


# --------------------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------------------
def load_cases(source):
  """Return a list of raw case dicts from a file path or `coval:<test_set_id>`."""
  if source.startswith("coval:"):
    return coval_pull(source.split(":", 1)[1])
  if not os.path.exists(source):
    sys.exit(f"source not found: {source}")
  if source.endswith((".jsonl", ".ndjson")):
    with open(source, encoding="utf-8") as handle:
      return [json.loads(line) for line in handle if line.strip()]
  if source.endswith(".json"):
    with open(source, encoding="utf-8") as handle:
      data = json.load(handle)
    if isinstance(data, dict):
      # tolerate {"test_cases": [...]} / {"data": [...]} wrappers
      for key in ("test_cases", "cases", "data", "rows"):
        if isinstance(data.get(key), list):
          return data[key]
      sys.exit("JSON object has no recognizable list of cases (test_cases/cases/data/rows)")
    return data
  if source.endswith((".csv", ".tsv")):
    delimiter = "\t" if source.endswith(".tsv") else ","
    with open(source, encoding="utf-8-sig", newline="") as handle:
      return list(csv.DictReader(handle, delimiter=delimiter))
  sys.exit(f"unsupported source extension: {source}")


def coval_pull(test_set_id):
  """Paginate every case of a Coval test set via the v1 API (read-only)."""
  api_key = os.environ.get("COVAL_API_KEY")
  if not api_key:
    sys.exit("coval: source requires COVAL_API_KEY in the environment")
  cases = []
  page_token = None
  while True:
    query = {"filter": f'test_set_id="{test_set_id}"', "limit": "50"}
    if page_token:
      query["page_token"] = page_token
    url = f"{COVAL_API_BASE}/v1/test-cases?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"x-api-key": api_key})
    try:
      with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    except urllib.error.HTTPError as error:
      sys.exit(f"coval API error {error.code}: {error.read()[:300]!r}")
    batch = payload.get("test_cases") or payload.get("data") or []
    cases.extend(batch)
    page_token = payload.get("next_page_token")
    sys.stderr.write(f"  pulled {len(cases)} cases...\n")
    if not page_token or not batch:
      break
  return cases


# --------------------------------------------------------------------------------------
# Normalization into canonical records
# --------------------------------------------------------------------------------------
def parse_pipe_description(description):
  """Parse Coval's pipe-delimited `description` (key=value | key=value) into a dict."""
  labels = {}
  for chunk in str(description or "").split("|"):
    if "=" in chunk:
      key, value = chunk.split("=", 1)
      labels[key.strip()] = value.strip()
  return labels


def first_str(value):
  """Coerce a field that may be a list (e.g. expected_behaviors) into a single string."""
  if isinstance(value, list):
    return str(value[0]).strip() if value else ""
  return str(value or "").strip()


def to_records(raw_cases, args):
  records = []
  for raw in raw_cases:
    input_str = first_str(raw.get(args.input_field))
    expected = first_str(raw.get(args.expected_field))
    description = raw.get("description", "")
    labels = parse_pipe_description(description) if args.parse_coval_description else {}

    label = labels.get(args.label_field) or str(raw.get(args.label_field, "") or "") or "unlabeled"
    pass_fail_raw = labels.get(args.pass_fail_field) or str(raw.get(args.pass_fail_field, "") or "")
    pass_fail = "fail" if pass_fail_raw.strip().lower().startswith("fail") else ("pass" if pass_fail_raw else "unknown")
    language = "cjk" if CJK_PATTERN.search(input_str) else "latin"

    if not input_str:
      continue
    records.append(
      {
        "input": input_str,
        "expected": expected,
        "description": str(description or ""),
        "labels": labels,
        "label": label,
        "pass_fail": pass_fail,
        "language": language,
      }
    )
  return records


# --------------------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------------------
def normalize_text(text):
  text = WORD_PATTERN.sub(" ", str(text).lower())
  return re.sub(r"\s+", " ", text).strip()


def shingles(text, size=3):
  norm = normalize_text(text).replace(" ", "")
  if len(norm) < size:
    return {norm} if norm else set()
  return {norm[i : i + size] for i in range(len(norm) - size + 1)}


def jaccard(set_a, set_b):
  if not set_a or not set_b:
    return 0.0
  intersection = len(set_a & set_b)
  union = len(set_a | set_b)
  return intersection / union if union else 0.0


def is_low_info(expected):
  expected = (expected or "").strip()
  return len(expected) < 15 or bool(NA_PATTERN.match(expected))


# --------------------------------------------------------------------------------------
# Optional embeddings (graceful fallback to Jaccard)
# --------------------------------------------------------------------------------------
def embed_texts(texts):
  """Return embeddings via OpenAI if available, else None to signal fallback."""
  api_key = os.environ.get("OPENAI_API_KEY")
  if not api_key:
    return None
  vectors = []
  try:
    for start in range(0, len(texts), 256):
      batch = texts[start : start + 256]
      body = json.dumps({"model": "text-embedding-3-large", "input": batch}).encode()
      request = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
      )
      with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read())
      vectors.extend(item["embedding"] for item in payload["data"])
    return vectors
  except Exception as error:  # noqa: BLE001 — any failure falls back to the heuristic
    sys.stderr.write(f"  embeddings unavailable ({error}); falling back to n-gram heuristic\n")
    return None


def cosine(vector_a, vector_b):
  dot = sum(x * y for x, y in zip(vector_a, vector_b))
  norm_a = sum(x * x for x in vector_a) ** 0.5
  norm_b = sum(y * y for y in vector_b) ** 0.5
  return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


# --------------------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------------------
def greedy_cluster(records, threshold, vectors=None):
  """Greedily cluster records by input similarity. Returns list of clusters (lists)."""
  clusters = []
  cluster_signatures = []  # (representative shingles, representative vector index)
  shingle_cache = [shingles(record["input"]) for record in records]
  for index, record in enumerate(records):
    placed = False
    for cluster_index, cluster in enumerate(clusters):
      rep_index = cluster[0]
      if vectors is not None:
        similarity = cosine(vectors[index], vectors[rep_index])
      else:
        similarity = jaccard(shingle_cache[index], shingle_cache[rep_index])
      if similarity >= threshold:
        cluster.append(index)
        placed = True
        break
    if not placed:
      clusters.append([index])
  # map indices back to records
  return [[records[i] for i in cluster] for cluster in clusters]


def canonical_of(cluster):
  """Pick the most representative case in a paraphrase cluster: longest, most-specific
  input with a substantive expected answer."""
  return max(cluster, key=lambda record: (len(record["expected"]), len(record["input"])))


def distill(records, args):
  report = {}
  total = len(records)

  # Step 1 — drop low-information rows.
  records = [record for record in records if not is_low_info(record["expected"])]
  report["dropped_low_info"] = total - len(records)

  # Step 2 — split boilerplate-convergence from scenario rows.
  # Group by normalized expected answer; a large group whose INPUTS are diverse is
  # boilerplate (one generic answer covering many unrelated asks) — NOT one scenario.
  by_answer = defaultdict(list)
  for record in records:
    by_answer[normalize_text(record["expected"])].append(record)
  boilerplate_groups, scenario_records = [], []
  for _, group in by_answer.items():
    distinct_inputs = len({normalize_text(r["input"]) for r in group})
    if len(group) >= args.boilerplate_min and distinct_inputs >= len(group) * 0.6:
      boilerplate_groups.append(group)
    else:
      scenario_records.extend(group)
  report["boilerplate_groups"] = len(boilerplate_groups)
  report["scenario_rows_before_dedup"] = len(scenario_records)

  # Step 3 — dedup scenario rows (exact + paraphrase), clustering WITHIN each label bucket.
  by_label = defaultdict(list)
  for record in scenario_records:
    by_label[record["label"]].append(record)
  deduped = []
  use_embeddings = args.embeddings == "on"
  for label, bucket in by_label.items():
    # exact-normalized dedup first
    seen, unique = set(), []
    for record in sorted(bucket, key=lambda r: (-len(r["expected"]), -len(r["input"]))):
      key = normalize_text(record["input"])
      if key not in seen:
        seen.add(key)
        unique.append(record)
    vectors = embed_texts([r["input"] for r in unique]) if use_embeddings else None
    threshold = args.embed_threshold if vectors is not None else args.jaccard_threshold
    for cluster in greedy_cluster(unique, threshold, vectors):
      deduped.append(canonical_of(cluster))
  report["scenario_rows_after_dedup"] = len(deduped)

  # Step 4 — stratified, failure-weighted selection up to target size.
  selected = []

  # 4a. boilerplate quota: one canonical per group, spread across labels, capped.
  boilerplate_reps = [canonical_of(group) for group in boilerplate_groups]
  boilerplate_reps.sort(key=lambda r: (r["label"], -len(r["expected"])))
  boilerplate_quota = min(args.boilerplate_quota, len(boilerplate_reps), args.target_size)
  selected.extend(_round_robin_by_key(boilerplate_reps, lambda r: r["label"], boilerplate_quota))

  remaining = max(0, args.target_size - len(selected))
  fails = [r for r in deduped if r["pass_fail"] == "fail"]
  non_fails = [r for r in deduped if r["pass_fail"] != "fail"]

  # 4b. failures first (highest signal — known agent misses).
  fail_budget = min(len(fails), round(remaining * args.fail_weight)) if fails else 0
  selected.extend(_round_robin_by_key(fails, lambda r: (r["label"], r["language"]), fail_budget))

  # 4c. fill the rest with passes/other, one-per-label medoid, spread across labels + language.
  pass_budget = max(0, args.target_size - len(selected))
  selected.extend(_round_robin_by_key(non_fails, lambda r: (r["label"], r["language"]), pass_budget))

  # 4d. if still short (e.g. few fails), top up from any leftover deduped rows.
  if len(selected) < args.target_size:
    chosen_ids = {id(r) for r in selected}
    leftovers = [r for r in deduped + boilerplate_reps if id(r) not in chosen_ids]
    selected.extend(_round_robin_by_key(leftovers, lambda r: (r["label"], r["language"]), args.target_size - len(selected)))

  # 4e. language quota — make sure minority language keeps representation.
  selected = _enforce_language_quota(selected, deduped + boilerplate_reps, args)

  report["selected"] = len(selected)
  report["selected_fail"] = sum(1 for r in selected if r["pass_fail"] == "fail")
  report["selected_cjk"] = sum(1 for r in selected if r["language"] == "cjk")
  report["selected_by_label"] = dict(sorted(_counts(selected, lambda r: r["label"]).items()))
  return selected, report


def _counts(records, key):
  counter = defaultdict(int)
  for record in records:
    counter[key(record)] += 1
  return counter


def _round_robin_by_key(records, key, budget):
  """Pick up to `budget` records, rotating across distinct key values for even coverage.
  Deterministic: groups and members are sorted."""
  if budget <= 0 or not records:
    return []
  groups = defaultdict(list)
  for record in records:
    groups[key(record)].append(record)
  for group in groups.values():
    group.sort(key=lambda r: (-len(r["expected"]), -len(r["input"]), r["input"]))
  ordered_keys = sorted(groups.keys(), key=lambda k: (-len(groups[k]), str(k)))
  picked, cursor = [], 0
  while len(picked) < budget and any(groups[k] for k in ordered_keys):
    group = groups[ordered_keys[cursor % len(ordered_keys)]]
    if group:
      picked.append(group.pop(0))
    cursor += 1
  return picked


def _enforce_language_quota(selected, pool, args):
  if args.min_minority_ratio <= 0:
    return selected
  cjk = [r for r in selected if r["language"] == "cjk"]
  target_cjk = round(len(selected) * args.min_minority_ratio)
  if len(cjk) >= target_cjk:
    return selected
  chosen_ids = {id(r) for r in selected}
  cjk_pool = [r for r in pool if r["language"] == "cjk" and id(r) not in chosen_ids]
  cjk_pool.sort(key=lambda r: (0 if r["pass_fail"] == "fail" else 1, -len(r["expected"])))
  latin_in_selection = [r for r in selected if r["language"] == "latin"]
  swaps = min(target_cjk - len(cjk), len(cjk_pool), len(latin_in_selection))
  for offset in range(swaps):
    selected.remove(latin_in_selection[-(offset + 1)])
    selected.append(cjk_pool[offset])
  return selected


# --------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------
def emit_ndjson(selected, source, out_path):
  lines = []
  for record in selected:
    provenance = [f"distilled from {source}"]
    for key in ("journey", "sub_topic", "next_agent_status", "sme_result"):
      if record["labels"].get(key):
        provenance.append(f"{key}={record['labels'][key]}")
    if not record["labels"]:
      provenance.append(f"label={record['label']}")
    line = {
      "input_str": record["input"],
      "expected_output_str": record["expected"],
      "description": " | ".join(provenance),
    }
    lines.append(json.dumps(line, ensure_ascii=False))
  text = "\n".join(lines) + "\n"
  if out_path and out_path != "-":
    with open(out_path, "w", encoding="utf-8") as handle:
      handle.write(text)
  else:
    sys.stdout.write(text)


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--source", required=True, help="Path to NDJSON/JSON/CSV, or coval:<test_set_id>")
  parser.add_argument("--out", default="-", help="Output NDJSON path (default: stdout)")
  parser.add_argument("--target-size", type=int, default=30, help="Number of representative cases to keep (10-50 recommended)")
  parser.add_argument("--input-field", default="input_str", help="Field holding the user utterance/scenario")
  parser.add_argument("--expected-field", default="expected_behaviors", help="Field holding the expected answer/behavior")
  parser.add_argument("--label-field", default="next_agent_status", help="Field/label used as the intent/route stratification axis")
  parser.add_argument("--pass-fail-field", default="sme_result", help="Field whose value starts with Pass/Fail")
  parser.add_argument("--parse-coval-description", action="store_true", help="Parse pipe-delimited key=value labels from Coval `description`")
  parser.add_argument("--embeddings", choices=["on", "off"], default="off", help="Use OpenAI embeddings for paraphrase clustering (needs OPENAI_API_KEY); default heuristic")
  parser.add_argument("--embed-threshold", type=float, default=0.85, help="Cosine threshold for embedding paraphrase clustering")
  parser.add_argument("--jaccard-threshold", type=float, default=0.5, help="Char-3gram Jaccard threshold for heuristic paraphrase clustering")
  parser.add_argument("--boilerplate-min", type=int, default=5, help="Min same-answer group size to treat as boilerplate-convergence")
  parser.add_argument("--boilerplate-quota", type=int, default=4, help="Max boilerplate/fallback cases to keep")
  parser.add_argument("--fail-weight", type=float, default=0.45, help="Fraction of the non-boilerplate budget reserved for SME-Fail cases")
  parser.add_argument("--min-minority-ratio", type=float, default=0.0, help="Min share of the minority language (e.g. 0.3 to keep ~1/3 CJK); 0 disables")
  args = parser.parse_args()

  sys.stderr.write(f"Loading {args.source} ...\n")
  raw_cases = load_cases(args.source)
  records = to_records(raw_cases, args)
  sys.stderr.write(f"Loaded {len(raw_cases)} raw rows -> {len(records)} usable records\n")

  selected, report = distill(records, args)

  sys.stderr.write("\n=== Distillation report ===\n")
  for key, value in report.items():
    sys.stderr.write(f"  {key}: {value}\n")
  sys.stderr.write(f"\nWrote {len(selected)} representative cases to {args.out}\n")
  emit_ndjson(selected, args.source, args.out)


if __name__ == "__main__":
  main()
