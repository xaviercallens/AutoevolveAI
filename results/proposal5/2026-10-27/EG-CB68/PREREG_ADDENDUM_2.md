# EG-CB68 preregistration addendum 2 (written 2026-10-31 ~14:45 UTC, before any arbitrary-root run at cap >= 35)

- Addendum 1 (sha256 acb7e2d9e7326eb2e688318681f0917fa297c27cdcf734a96935e063057cf670, hashed 2026-10-28 17:53 UTC)
  set a 24 h wall-clock deadline of 2026-10-29 17:06 UTC for the exploratory extension.
- The producer session was then halted by an external API spend limit from about 2026-10-28 18:30 UTC to 2026-10-31 14:40 UTC.
  No EG-CB68 computation ran in that gap, apart from the batch already launched (run_main.sh, run_controls2.sh), which finished
  unattended. No arbitrary-root run at cap >= 35 has been started.
- CPU use so far is about 2 core-hours of the 48 core-hour box.
- **Change, made before any extension run:** the wall-clock deadline for the extension moves to 2026-11-01 14:45 UTC.
  Everything else in addendum 1 is unchanged: the stop rule (projection must fit in the remaining core-hours and wall time),
  the claims, the tiers, the wording, and the cores (2 and 3).
- In the write-up, this is reported as a deviation.
