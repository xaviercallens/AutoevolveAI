theorem problem_20_triangle_inequality {X : Type*} [MetricSpace X] (x y z : X) : 
    dist x z ≤ dist x y + dist y z :=
  dist_triangle x y z