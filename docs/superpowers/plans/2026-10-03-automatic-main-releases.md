# Automatic main releases implementation plan

**Goal:** Publish each successfully tested merge to main with the next stable version, reviewed PR release notes, current install information, and a Milkbeat core rebuild.

**Scope:** Extend the existing Android CI/CD workflow. Preserve the projectM pin, preset measurements, signing secrets, APK/core AAR names, and existing build/test commands. Keep the original shared workspace untouched.

## Requirements and decisions

- Allocate each patch/code deterministically from first-parent main history after the configured base commit. The first merge maps to base version 2.1.5/code 37, and later merges advance both together. Fetch semantic tags to detect collisions, find earlier reachable releases and verify historical Android codes. This handles queue ordering variations and retries without publishing older source as a newer version.
- Queue workflow runs (`queue: max`, no cancellation), including main releases, to avoid competing version allocation and skipped merges.
- Require a substantive `## Release notes` section in new PRs. Validate presence and placeholders; factual accuracy and user-facing wording remain review responsibilities.
- Collect merged PR notes since the previous version tag. Preserve fuller descriptions for historical PRs without the new section, and use actual commit summaries when there is no PR. Never execute PR text or invent feature claims.
- Derive Downloader code from the canonical README; append fixed/latest and versioned APK/core AAR URLs, checksum information, and the comparison link. Keep the existing release notes file as an archive and the prepared 2.1.5 notes as historical context.
- Publish only successful main push/manual runs; PR and feature-branch runs remain test artifacts. Require release signing for publishing runs. Make release creation/upload safe to retry against the same commit/tag.
- Trigger Milkbeat after a core release; skip a core already consumed by its latest release and fail visibly if the dispatch token is missing.

## Implementation units

1. Release helpers and standard-library unit tests under `.github/scripts/`: version allocation, PR note extraction/validation, safe GitHub API handling, source-grounded note generation, idempotent publication, and downstream dispatch decisions. Test missing/malformed sections, old PR fallback, quoted/untrusted text, version/code floors, retries, feature branches, first releases, and Downloader/link output.
2. Workflow and Gradle integration: full tag history, queued runs, helper invocation, actual version overrides, signed APK/core build, checksums, publication and Milkbeat dispatch. Verify workflow syntax, locally build the generated version, and check PR CI.
3. Author guidance in root `AGENTS.md`, `.github/PULL_REQUEST_TEMPLATE.md`, README and releasing docs: write factual user-facing release notes, avoid routine version bumps, explain automatic versions/retries/install links and release-line changes.
4. Commit and open a PR with its required release-notes section. Monitor checks and report a concrete, reviewable result.

**Implementation status:** Units 1–3 are implemented; helper tests, API-boundary publication tests, release-note preview, Android builds and JVM tests are verified. Workflow lint passes except that actionlint 1.7.12 does not yet recognize GitHub’s documented `queue: max` keyword; that single schema warning is excluded, and GitHub PR CI validates the actual workflow. Unit 4 is the final handoff.

## Verification

Run the helpers' unit tests, validate workflow YAML with actionlint where available, preview notes from real merged PRs without publishing, run release JVM tests/build, and monitor the feature PR checks. No preset remeasurement.
