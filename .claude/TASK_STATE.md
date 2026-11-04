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
- [ ] subjective review (blind batches via subagents)
- [ ] triage
- [ ] execute queue

## Subjective review run
- Run dir: .desloppify/subagents/runs/20261104_184513 (20 prompts; outputs -> results/batch-N.raw.txt)
- Agents: Sonnet, waves of 5. Wave1=1-5, wave2=6-10, wave3=11-15, wave4=16-20.
- After all done: `desloppify review --import-run .desloppify/subagents/runs/20261104_184513 --scan-after-import`
- If interrupted: check which results/*.raw.txt exist; rerun only missing batches.
- Wave1 (1-5) DONE, spot-checked: evidence concrete. Wave2 (6-10) launched.

## Notes for execute phase
- build_elite_seo_operating_kit.py build_docs() (~790 LOC of embedded md) regenerates references/kit/*.md byte-identical to committed files (verified in scratch copy: no git diff). Strong candidate: make .md files source of truth, drop embedded copies.
- Deps present: openpyxl 3.1.5, python-docx 1.2.0. pytest not checked yet.
- Contract: SKILL.md:48 + README.md:58 say "edit generator scripts, never generated files". Extracting build_docs md => must update both docs. Tell user (authoring workflow change).
- pytest NOT installed (needed for test health; pip install pytest, dev-only).
