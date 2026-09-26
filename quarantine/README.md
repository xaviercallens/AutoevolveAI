# Quarantine Directory

This directory holds modules that reported success without doing the work. These are discovered during remediation audits and quarantined to prevent them from affecting other parts of the codebase.

## Constraints

- Nothing in this directory may be imported by `anse/`, `scripts/`, or `tests/` (except by tests explicitly asserting it is NOT imported).
- Each entry must be documented with its original path, the audit finding, and the date of discovery.

## Entries

(Entries added as modules are identified during audits)
