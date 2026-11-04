# TASK STATE: desloppify quality pass

## Objective
Raise desloppify **strict** score on highbaud/elite-seo-skill. Branch: `desloppify-quality`.
User asks: run desloppify loop (next -> fix -> resolve), take notes, use cheaper models where quality not hurt.

## Setup (done)
- Clone: /home/user/elite-seo-skill (shallow). Branch `desloppify-quality` created.
- `pip install --upgrade "desloppify[full]"` (v1.0); `desloppify update-skill claude` -> .claude/skills/desloppify/SKILL.md
- `.desloppify/` added to .gitignore. No excludes needed (no vendor/build dirs; code = scripts/*.py only).

## Resume commands
```
pip install --upgrade "desloppify[full]"   # if new container
cd /home/user/elite-seo-skill && desloppify next
```
Note: .desloppify/ state is NOT committed; a new container must rescan (`desloppify scan --path .`) and redo subjective review.

## Baseline scan (2026-11-04)
strict 10.5 | objective 42.2 | code quality 81.8 | dup 100 | file health 80 | security 100 | test health 0
34 open issues. Subjective dims unassessed (0%).

## Progress log
- [x] subjective review: 20/20 batches imported (`--import-run ... --scan-after-import`). 37 review items added.
  Post-review: strict 64.9 | mechanical pool 42.2 | subjective pool 72.5
  Subj: abstraction 90, ai_debt 89, api 70, authz 96, contracts 79, convention 82, xmodule 82, deps 88,
        design 78, errors 68, high_eleg 74, incomplete_mig 96, init_coupling 95, logic 82, low_eleg 68,
        mid_eleg 71, naming 78, pkg_org 88, test_strategy 22, type_safety 38
  Biggest drags: test health 0% (-13.3), type safety 38 (-4.5), mid elegance (-3.9), high elegance (-3.5)
  Do NOT rescan mid-queue (regenerates IDs, breaks triage). Finish queue first.
- [ ] triage
- [ ] execute queue

## Subjective review run
- Run dir: .desloppify/subagents/runs/20261104_184513 (20 prompts; outputs -> results/batch-N.raw.txt)
- Agents: Sonnet, waves of 5. Wave1=1-5, wave2=6-10, wave3=11-15, wave4=16-20.
- After all done: `desloppify review --import-run .desloppify/subagents/runs/20261104_184513 --scan-after-import`
- If interrupted: check which results/*.raw.txt exist; rerun only missing batches.
- Wave1-3 (1-15) DONE except b13 (retry running; 1st attempt wrote nothing). b12,b15 returned JSON in msg -> I copied it verbatim to results. Wave4: 16-19 launched, 20 after. Use strict "must Write file" prompt.
- Scores so far: b1 cross_module_architecture=82.0; b2 high_level_elegance=74.0; b3 convention_outlier=82.0; b4 error_consistency=68.0; b5 naming_quality=78.0; b6 abstraction_fitness=90.0; b7 dependency_health=88.0; b8 low_level_elegance=68.0; b9 mid_level_elegance=71.0; b10 test_strategy=22.0

## Notes for execute phase
- build_elite_seo_operating_kit.py build_docs() (~790 LOC of embedded md) regenerates references/kit/*.md byte-identical to committed files (verified in scratch copy: no git diff). Strong candidate: make .md files source of truth, drop embedded copies.
- Deps present: openpyxl 3.1.5, python-docx 1.2.0. pytest not checked yet.
- Contract: SKILL.md:48 + README.md:58 say "edit generator scripts, never generated files". Extracting build_docs md => must update both docs. Tell user (authoring workflow change).
- pytest NOT installed (needed for test health; pip install pytest, dev-only).
- BUG to fix: seo_gsc_analyzer read_rows: blank position -> 0.0 -> treated as rank 1 (b11).

## Execute phase plan (51 open: 37 review + 14 mechanical)
Shared modules (me, DONE): scripts/kit_common.py (SKILL_ROOT/ASSETS_DIR/CSV_TEMPLATE_DIR, atomic_write, write_csv),
scripts/workbook_spec.py (STUB: headers_for(title) for 3 analyzer tabs), tests/conftest.py (adds scripts/ to sys.path). pytest installed.
Decision: references/kit/*.md become hand-edited source; build_docs() removed (verified identical output first). Update README.md + SKILL.md + kit README paths (me).
Streams (Sonnet agents, same worktree, disjoint files, agents do NOT commit / NOT run desloppify resolve):
- A analyzer: owns scripts/seo_gsc_analyzer.py, tests/test_seo_gsc_analyzer.py. Imports workbook_spec.headers_for, kit_common.write_csv.
- B builder: owns scripts/build_elite_seo_operating_kit.py, scripts/workbook_spec.py (fill all tabs, keep headers_for API), tests/test_build_kit.py. Must reproduce assets byte-identical (CSVs) / content-identical (xlsx).
- C docx: owns scripts/build_seo_report_docx.py, tests/test_build_report_docx.py.
- Me after: requirements*.txt, README/SKILL.md/kit README, contract test, review, resolve items, commit, rescan.
- Agents A/B/C launched (Sonnet, background). Me: DONE (uncommitted, commit with agent code): requirements.txt, requirements-dev.txt, README.md regen+tests sections, SKILL.md automation line, references/kit/README.md asset paths.
  If session dies before agents finish: check `git status`; review each script vs its spec in this file; run `python3 -m pytest -q`.
- Stream C (docx) DONE + committed; verified identical (49 paras, 5 tables), 7 tests pass.
- Stream A (analyzer) DONE + committed; old vs new byte-identical on 1800 random rows; 29 tests pass.
- Stream B (builder) DONE + committed c1f255d: assets identical (31 CSV byte-equal, xlsx 0 diffs). I unified CSV writing via kit_common.write_csv(lineterminator=).
- Extra fixes (me): analyzer --out-dir alias; builders catch OSError. 49 tests pass.
- NEXT: resolve all review items w/ notes (desloppify plan resolve <id> --note ... --confirm), then rescan.
- All 37 review items resolved (in plan order; short notes get silently refused, check for 'Resolved 1 issue'). commit-log recorded. NEXT: desloppify scan.

## Cycle 1 result (scan after fixes)
strict 70.1 | overall 79.1 | objective 98.8 (from 42.2). 3 open = sys_exit_in_library false positives on `sys.exit(main())` in __main__ guard (desloppify detector ignores main guard; _CLI_FILENAMES only). Left as-is deliberately (not gaming via raise SystemExit). Tell user; upstream issue needs their OK.
Subjective scores are stale (pre-refactor). NEXT: re-review all dims: `desloppify review --run-batches --dry-run --force-review-rerun` -> Sonnet agents, strict "must Write file" prompt, waves of 5.
