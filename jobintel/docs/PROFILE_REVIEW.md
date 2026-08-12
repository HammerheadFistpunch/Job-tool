# Patrick Profile Review

The first structured profile is active at
`data/input/Profiles/patrick_profile.json`. It contains established career facts
and conservative search rules. It deliberately sends uncertain cases to
`needs_review` instead of guessing.

## Active rules

- Home area: Sandy, Utah; on-site and hybrid roles within 30 miles.
- Fully remote United States roles are accepted.
- Relocation is not accepted.
- Absolute base-salary floor: $75,000.
- Target base salary: $90,000-$130,000.
- Strong role families: technical marketing, technical product marketing,
  strategic communications, content strategy, and adjacent senior work.
- Commission-only work, primarily cold-calling roles, forced overtime, and
  explicit SDR/junior-sales titles are hard rejections.
- Missing salary is provisionally eligible; unclear location data requires review.

## Resolved policy — profile 2026-08-12.2

- Hybrid office attendance has no hard maximum.
- Routine travel up to and including 25% is accepted; higher requirements are
  ineligible.
- Full-time, contract-to-hire, and fixed-term employment are accepted.
  Explicit part-time, temporary, W-2 contract, or 1099 arrangements are
  ineligible; ambiguous contract language requires review.
- Jobs without a posted salary are provisionally eligible. A stated maximum
  below the $75,000 floor remains ineligible.
- Missing required credentials require review unless a license or clearance is
  legally mandatory, in which case the job is ineligible.
- Strong senior individual-contributor roles rank equally with manager roles.

All previously unresolved profile decisions are now closed. Future policy
changes should increment `profile_version` so the review queue reevaluates jobs.
