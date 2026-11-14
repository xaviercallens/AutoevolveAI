# LT_C deviations

- None to the preregistered H-LT5 campaign (code sha256 matched the preregistration before launch; 12 cells x 12 restarts, seeds 5000..6111, 1 process, 2 threads).
- H-LT2 main run executed at 15:00-15:02 UTC with the frozen structure_lt2.py on the files then present (snapshot recorded in h_lt2.json); no change to rule.
- SUPPLEMENT (exploratory, NOT part of the preregistered verdict, added after seeing the KILLED statuses): h_lt2_explore.py recomputes C with tighter regions (tr W > 1e-2, 1e-1, 5e-1 of max) for the KILLED rows, to locate where the non-commutativity sits. Labelled exploratory in the report; the verdict is the preregistered one.
- Note on scope: the preregistered H-LT2 rule counts all analysed rows including the gamma = 1.5 control cells of LT_B. gamma = 3/2 is outside the open range (1/2, 3/2) of the claim, so the report states the verdict both with and without those rows.
