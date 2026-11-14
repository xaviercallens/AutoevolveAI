import Autoresearch.DyadicHilbert

namespace AutoresearchDyadic

def w4row0 : List ℤ := [1, -1, 1, -1, 1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1]

#eval (List.range 16).map (fun j => (ofTable (n := 4) [w4row0] : Fn 4)
  ((false, false, false, false, ()) : Bool × Bool × Bool × Bool × Unit)
  (((j / 8 % 2 == 1), (j / 4 % 2 == 1), (j / 2 % 2 == 1), (j % 2 == 1), ()) : Bool × Bool × Bool × Bool × Unit))

#eval idx 4 ((false, true, false, false, ()) : Bool × Bool × Bool × Bool × Unit)
#eval idx 2 ((true, false, ()) : Bool × Bool × Unit)

end AutoresearchDyadic
