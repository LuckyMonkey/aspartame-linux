# Aspartame Activity Contract

Aspartame owns the Activity experience. Sugar Labs and Sugarizer are upstream
sources we may borrow from; neither defines Aspartame user-facing runtime.

## Runtime types

Every Activity entry has a runtime type:

- native-sugar: a native Sugar .activity bundle launched by sugar-activity3.
- sugarizer-web: a Sugarizer-style web Activity. It is not a native Sugar
  bundle and is not launched by sugar-activity3.
- aspartame-native: an Aspartame-owned Activity following the native contract.
- experimental: an entry under evaluation and not promised to users.

The source is provenance. The runtime type is what Aspartame promises.

## Common metadata

| Field | Meaning |
| --- | --- |
| id | Stable Activity identifier |
| name | User-facing name |
| version | Activity version |
| runtime | Aspartame runtime type |
| source | Upstream or local provenance |
| source_revision | Exact source/catalog revision |
| icon | Activity icon reference |
| summary | Short plain-language description |
| help | Stable help/documentation target |
| run_status | Review state |
| rating | Five-point readiness rating |
| installed | Whether this runtime is installed |
| screenshot | Evidence path, when tested |

Native metadata originates in activity.info. Sugarizer metadata originates in
the pinned activities.json. Aspartame adds the common fields without rewriting
either upstream format.

## Activity quality contract

An Activity should:

1. launch through its declared runtime;
2. present a Sugar-consistent toolbar and lifecycle;
3. expose a plain-language summary and help target;
4. preserve work through Journal or its declared storage model;
5. handle stop, resume, and relaunch predictably;
6. use symbolic/stateful artwork without arbitrary decorative noise;
7. provide a testable screenshot and runtime log;
8. declare known dependencies and network requirements;
9. keep advanced capability available without making it the primary path.

An Activity may remain marked needs-work while it is usable. Ratings describe
readiness, not popularity, and never authorize automatic deletion.

## Borrowing policy

Borrowing is evaluated in this order:

1. interaction idea;
2. metadata, help, or localization pattern;
3. artwork or code under compatible licensing;
4. complete implementation only when its runtime and maintenance cost fit
   Aspartame.

A Sugarizer web Activity remains web-compatible until a native implementation
has been deliberately created and tested.

## Current catalog

The machine-readable review inventory is docs/activity-reviews/REVIEWS.tsv.
It contains native Sugar entries and the pinned Sugarizer catalog. The review
pipeline preserves per-user ratings in the guest separately from this source
catalog.

## Future manager behavior

The Activity Manager should present one Aspartame list while making runtime type
clear in developer/detail views:

- installed native Activities are launchable now;
- catalog-only web Activities are candidates, not falsely installed;
- ratings and help metadata are shared;
- removal is allowed only for an installed managed bundle;
- a web entry is not removable through the native bundle remover.

This keeps Aspartame coherent while allowing useful borrowed work to enter
deliberately.
