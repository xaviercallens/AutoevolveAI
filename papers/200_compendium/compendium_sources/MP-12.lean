theorem problem_12_cayley_hamilton {n : Type*} [DecidableEq n] [Fintype n] {R : Type*} [CommRing R] 
    (M : Matrix n n R) : aeval M M.charpoly = 0 :=
  Matrix.aeval_self_charpoly M