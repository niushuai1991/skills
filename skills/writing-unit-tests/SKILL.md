---
name: writing-unit-tests
description: Reference principles for writing clean, isolated unit tests. Use when writing, adding, or reviewing unit tests — especially before running tests that exec real scripts/binaries or touch global config, env vars, HOME, the clock, the network, or files outside a temp dir. Headline rule — isolate anything the code under test mutates outside its own memory (e.g. ~/.gitconfig, env, HOME, cwd) by redirecting it to a throwaway sandbox, so tests never clobber host/developer state.
---

# Writing Unit Tests

Hard-won principles worth scanning before writing or running a unit test. High-signal only — basics (AAA, one-behavior-per-test, name-by-behavior) are assumed known.

## 1. Isolate everything the code mutates outside its own memory  ← the one that bites

If the code under test — or any script/binary it execs — writes to global or shared state, **redirect that target to a throwaway sandbox for the duration of the test.** Otherwise the test silently clobbers the developer's real environment, and the damage is invisible until something else breaks.

| What the code touches | Isolate by |
|---|---|
| Files under `HOME` (`~/.gitconfig`, `~/.npmrc`, `~/.aws/…`, `~/.config/…`) | run with `HOME="$tmp"`; or the tool's own override: `GIT_CONFIG_GLOBAL=`, `npm_config_userconfig=`, `AWS_*`, `XDG_CONFIG_HOME=` |
| Environment variables | explicit env dict in a subprocess; or save → mutate → restore in a `finally`/teardown |
| Current working directory | `cd "$tmp"` … restore on teardown |
| System clock / dates | inject/freeze a clock; never call real `now()` in the code path under test |
| Network / external services | mock/stub; or reclassify as an integration test (§2) |
| Anything outside the test's temp dir | write **only** under a per-test temp dir |

**Concrete lesson:** a test ran the real `entrypoint.sh` on the host to check its clone logic. That script calls `git config --global user.name …`, which overwrote the developer's real `~/.gitconfig` and changed their git identity — every time the test ran. Fix: run the script with `HOME` pointed at a temp dir (so `--global` lands in `$tmp/.gitconfig`), or don't exec the real global-mutating entrypoint on the host at all.

**Rule of thumb:** a unit test must run twice in a row, in parallel with a copy of itself, on a fresh machine, and leave zero trace outside its own temp dir. If it can't, it isn't isolated — fix the leak, don't document it.

## 2. Respect the unit / integration boundary

If a test needs a real service, real filesystem-with-shared-state, the real network, or a real DB, it is an **integration test**: label it, keep it out of the fast unit suite, and **still sandbox its writes**. Don't smuggle host-mutating behavior into a "unit" test just to avoid standing up a container — that's exactly how §1 leaks happen.

## 3. Determinism (no flakiness)

- No real time, no real randomness — freeze/inject both.
- No `sleep`-until-thing; wait on a condition or signal.
- No dependence on test execution order or parallelism.
- Same inputs → same result, every run, every machine.

## 4. Read-back before claiming done

Before declaring tests green, actually run them and read the output. Asserting "it should pass" is not verification — green output is. (See the `verify` / `verification-before-completion` habits.)
