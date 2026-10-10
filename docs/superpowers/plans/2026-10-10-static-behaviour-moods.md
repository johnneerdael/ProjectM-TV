# Static behaviour and mood implementation plan

> Use subagent-driven-development for independent evidence modules and executing-
> plans for coupled integration in the existing worktree. The user approved the
> direction and activated the goal; no additional approval gate is needed.

**Goal:** Improve source-only activity classification by quantified flashing,
motion and prominence, preserving uncertainty and source semantics.
**Architecture:** Extend typed source analysis, export three evidence groups and
join them into a versioned behaviour scorer. Reuse optional proof/symbolic/compiler
facilities selectively, with no display simulation.
**Tech stack:** Existing Python analyzer, pinned ProjectM-TV readers, SymPy/Z3,
optional compiler IR; unchanged Android/AAR.

## 1. Baseline and contract
- [ ] Read current activity/mood/extraction paths and save fixed2000/100 identities.
- [ ] Record current quantified fields and unassigned bands; freeze new thresholds
  as preference assumptions independently of the cohort/human labels.
- [ ] Define evidence groups (`flashing`, `motion`, `prominence`), physical units,
  interval/premise/provenance fields and explicit consumer signatures.

## 2. Mathematical producers (independent files)
- [ ] Flash evidence: first controls for high/low contrast, unreachable gates,
  smooth high-frequency pulses, alpha/modulo crossings and shared event schedules;
  then use qualified source ranges/derivatives and predicate proofs.
- [ ] Motion evidence: first translation/rotation/zoom combined cases, inverse
  map direction, zero-neutral, singular/spatial/unknown cases and explicit FPS;
  then reuse native transport and source derivative machinery.
- [ ] Prominence evidence: first tiny/transparent/offscreen/viewport-covering/
  attenuated/overlapping cases; then derive clipping/material/transfer intervals
  while preserving unresolved history and contrast.
- [ ] Run focused tests after each producer and repair/retest exact failures.

## 3. Consumer and preference mapping
- [ ] Add `static_behaviour` to source description; preserve existing fields and
  include context/policy identities in export/cache identity.
- [ ] Implement `score_static_behaviour(evidence, preferences=None)` with activity
  range, bands/reasons and missing contributions. Never fill p95 fields from
  deterministic upper bounds or promote estimates into native certification.
- [ ] Test calm/mid/intense controls and transparency/disconnection/unknown
  rejection, overlap25–30/70–75 and strict no-flash Chill eligibility.
- [ ] Document schema/units/assumptions and update AGENTS in the same branch.

## 4. Real source qualification and continued gap reduction
- [ ] Compare baseline/new facts and scores on unchanged fixed2000; report exact
  affected filenames/hashes, unknown causes by prevalence and component visibility.
- [ ] Recheck known human examples without fitting to their individual outcomes.
- [ ] Prioritize any missing frequent flash/motion/prominence calculation and
  implement/retest it before declaring completion.
- [ ] Run prepared suite, schema checks,100-source paired export and independent
  spec/correctness review; freeze source during each qualification run.
- [ ] Commit/push increments, export report/evidenceZIP in Downloads, audit full
  objective. Leave goal active when required behaviour remains incomplete.

Useful commands (prepared environment required):
```sh
MILK_SYMBOLIC_PYTHON=/Users/jneerdael/Scripts/source-analysis-evaluation/python-env/bin/python MILK_PROOF_PYTHON=/Users/jneerdael/Scripts/source-analysis-evaluation/python-env/bin/python build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer/test_source_activity.py tools/milk-analyzer/test_source_vertex_motion.py tools/milk-analyzer/test_mood_scoring.py -q
```
All final adapter/environment inputs remain in the completed component
qualification JSON under build/preset-corpus; revalidate before full-suite use.
