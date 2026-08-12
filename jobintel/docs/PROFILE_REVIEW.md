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
- Missing salary or unclear eligibility data requires review.

## Decisions still needed

1. Maximum number of required office days per week for hybrid roles.
2. Maximum acceptable travel percentage.
3. Which contract, part-time, temporary, and contract-to-hire arrangements are
   acceptable.
4. Whether postings with no salary should remain `needs_review` or be treated as
   provisionally eligible.
5. Which required credentials or security-clearance conditions should reject a
   job rather than require review.
6. Whether senior individual-contributor roles should rank equally with manager
   roles or slightly below them.

These decisions are not blockers for testing the evaluator or building the
review queue. Updating any of them should increment `profile_version` so stored
jobs can be reevaluated against the new policy.
