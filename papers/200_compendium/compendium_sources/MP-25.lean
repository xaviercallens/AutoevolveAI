theorem problem_25_heine_borel {α : Type*} [MetricSpace α] [ProperSpace α] (s : Set α) :
    IsCompact s ↔ IsClosed s ∧ IsBounded s :=
  Metric.isCompact_iff_isClosed_bounded