# Compatibility baseline

Date: 2026-09-24

This record defines the OpenSpec release used for this package. It also records
the feasibility callout required before implementation.

## OpenSpec release

The installed executable is `/usr/bin/openspec`. It resolves to the published
package `@fission-ai/openspec`.

- Installed version: `1.13.2`
- Published package version: `1.13.2`
- Published `latest` tag: `1.13.2`
- Selected compatibility baseline: `@fission-ai/openspec` `1.13.2`
- Baseline source: the installed package at
  `/usr/lib/node_modules/@fission-ai/openspec`
- Baseline source date: 2026-09-24

The baseline uses the installed package and its published package metadata. It
does not use unreleased source from the OpenSpec `main` branch.

The baseline checks used these commands and files:

- `openspec --version`
- `npm` registry metadata for `@fission-ai/openspec`
- `schemas/spec-driven/schema.yaml`
- `dist/core/project-config.js`
- `dist/core/profiles.js`
- `dist/core/config-schema.js`
- `dist/core/init.js`
- `README.md`

## Supported OpenSpec surfaces

OpenSpec 1.13.2 supports the surfaces that this package uses:

- `openspec/config.yaml` selects the project schema.
- `context` supplies project context to artifact instructions.
- `rules` supplies extra rules for artifact IDs.
- `operations.apply.guidance` supplies advisory Apply guidance.
- `operations.archive.guidance` supplies advisory Archive guidance.
- `openspec config profile` selects the global workflow profile.
- A custom profile can list `verify` in `workflows`.
- `openspec update` writes the selected generated workflow files.
- User-level skills can live in the Codex shared `.agents/skills` location.

The stock `spec-driven` schema contains `proposal`, `specs`, `design`, and
`tasks` artifacts. It contains no `verification.md` artifact. Its Apply phase
tracks `tasks.md`.

The stock core profile does not include `verify`. The installed global Codex
configuration uses `profile: custom`, `delivery: skills`, and includes the
`verify` workflow. This confirms that the supported profile and delivery
surfaces expose the native Verify skill without a replacement implementation.

## Feasibility callout

A feasibility callout compares each target need with the stock schema, project
configuration, user-level skills, and a small bootstrap. The result below is
the implementation boundary for this change.

| Target need | Stock surface | Result | Evidence and boundary |
| --- | --- | --- | --- |
| Keep the stock workflow | `schema: spec-driven` | Fits | `schemas/spec-driven/schema.yaml` is installed and remains unchanged. |
| Add project context | `context` in `openspec/config.yaml` | Fits | `dist/core/project-config.js` reads the field and passes it to artifact instructions. |
| Add per-artifact rules | `rules` in `openspec/config.yaml` | Fits | The parser accepts a map of artifact IDs to string lists. |
| Add Apply and Archive policy | `operations.*.guidance` | Fits | OpenSpec 1.13.2 reads `apply` and `archive` guidance as advisory input. |
| Expose native Verify | Custom profile and `openspec update` | Fits | `dist/core/profiles.js` lists `verify`, and the package README documents the profile path. |
| Add reusable agent behavior | Codex user-level skill | Fits | The supported host exposes `~/.agents/skills`. |
| Run setup across repositories | Thin bootstrap | Fits | The bootstrap can invoke normal `openspec init`, merge YAML, select the profile, and run `openspec update`. |
| Preserve existing project files | Bootstrap preflight and rollback | Fits as custom support | The helper owns only its policy and profile changes. It does not replace generated files or project rules. |
| Add optional Grill Me discovery | Thin adapter skill | Fits as custom support | The adapter can delegate to the installed `grill-me` skill and consume its distilled result. |
| Add optional Simple English discovery | Codex user-level skill | Fits as custom support | The installer can discover `skills/simple-english/SKILL.md` without copying or owning the upstream file. |
| Stage Grill output before a change | Non-root staging metadata | Fits as custom support | The adapter can preserve `.grill` source and add an identity record outside the OpenSpec artifact graph. |
| Attach Grill output to a change | Change-local `grill.md` | Fits as custom support | The file remains supplemental context and is not added to the schema. |
| Require applicable Human UAT | Guidance and normal task checkboxes | Fits as advisory policy | OpenSpec tracks checkboxes. The user must provide the pass or waiver record. Guidance cannot self-accept UAT. |
| Invalidate only affected UAT | Guidance and durable task records | Fits as advisory policy | The package can describe impact review. Native OpenSpec does not provide scenario impact tracking. |
| Keep Verify fresh | Apply and Archive guidance | Fits as advisory policy | The package can require evidence for the latest substantive state. Guidance does not create a Verify database. |
| Protect Archive | Archive guidance and native task checks | Fits as advisory policy | The package can recommend Verify and name incomplete UAT. Native Archive remains authoritative. |
| Explain source isolation | README | Fits | OpenSpec change folders do not isolate source files. Git owns branches and worktrees. |
| Test upgrades | Package tests and smoke checks | Fits | Tests can inspect the selected surfaces and the installed Grill contract. |

All target needs fit the supported surfaces. No requirement requires a custom
schema, replacement command, custom lifecycle implementation, custom Apply
implementation, custom Verify implementation, custom Archive implementation,
or task scheduler. Configuration guidance is sufficient for Apply behavior.
This change therefore stays inside the stated non-goals.

## Grill Me dependency contract

The upstream dependency is:

- Repository: `satya-janghu/agent-skills`
- Skill path: `skills/grill-me/SKILL.md`
- Observed source commit: `d4505d01b2272129d83da70e2b66a48b2588953a`
- Skill name: `grill-me`

The adapter depends on this small public contract:

1. The installed skill is discoverable by the host.
2. The agent can invoke the skill by its name or documented host syntax.
3. The skill returns distilled decisions and context after its question process.
4. The result can be recorded with the required `grill.md` sections.

The adapter does not copy the upstream question loop, prompts, lens list,
logging prose, or exact file slug rules. The adapter does no implementation
work. If the dependency is missing, the adapter reports the missing skill and
leaves source material unchanged.

## Simple English dependency contract

The upstream dependency observed on 2026-09-27 is:

- Repository: `AminBlg/SimpleEnglish`
- Skill path: `skills/simple-english/SKILL.md`
- Observed source commit: `79b590fc8596523d92c26b1ea7e33236606ef069`
- Observed skill version: `2.1.0`
- Skill name: `simple-english`

The installer uses this name-discovery contract:

1. It reads `<skills-dir>/simple-english/SKILL.md` first.
2. It supports a nested `simple-english/SKILL.md` path under the selected
   skills directory.
3. It reads the `name` field in the skill front matter.
4. It reports the skill as missing when the declared name does not match
   `simple-english`.
5. It reports the result as an advisory prerequisite. It does not copy,
   update, own, or remove the upstream file.

The installer does not inspect the upstream plugin, hook, or output style. It
uses the standalone skill file only.

## Host discovery

The supported host for this package is Codex. OpenSpec 1.13.2 identifies Codex
with the project skill directory `.agents/skills`. This environment also
provides the user-level skill directory `~/.agents/skills`.

The package installs the custom skill in the discovered user-level directory.
It installs the executable in a user-level directory already present in
`PATH`, or reports that no supported executable directory is available. It
does not guess another host layout.
