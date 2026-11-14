def wmean (s : Finset ι) (n f : ι → K) : K :=
  (∑ i ∈ s, n i * f i) / ∑ i ∈ s, n i

def wcov (s : Finset ι) (n f g : ι → K) : K :=
  (∑ i ∈ s, n i * (f i - wmean s n f) * (g i - wmean s n g)) / ∑ i ∈ s, n i

def wvar (s : Finset ι) (n f : ι → K) : K :=
  wcov s n f f

def zbarNext (s : Finset ι) (n w z' : ι → K) : K :=
  wmean s (fun i => n i * w i) z'

def wbarNext (s : Finset ι) (n w : ι → K) : K :=
  zbarNext s n w w
