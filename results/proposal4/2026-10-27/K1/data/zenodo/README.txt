===============================================================================
<<<>><<>><<>><<>><<>><<>><<| NIST Data Publication |>><<>><<>><<>><<>><<>><<>>>
===============================================================================
Data for Intrinsic DAC calculations


<<<>><<>><<>><<>><<>><<>><<>>| Author and Version |<<>><<>><<>><<>><<>><<>><<>>>

Authors:
  Austin McDannald
    austin.mcdannald@nist.gov
    National Institute of Standards and Technology
    Materials Measurement Science Division
  Daniel W. Siderius
    daniel.siderius@nist.gov
    National Institute of Standards and Technology
    Chemical Sciences Division

Version 1.0
DOI: 10.18434/mds2-3687

<<<>><<>><<>><<>><<>><<>><<>>| Dataset Description |<<>><<>><<>><<>><<>><<>><<>>>


The contents of this file include the results of Grand Canonical Monte Carlo (GCMC) simulations, predictions of the Specific Heat Capacities (CV), and Intrinsic Direct Air Capture (DAC) calculations for Metal Organic Framework (MOF) sorbents.

GCMC Calculation Results:
The results of the GCMC calculations for the Henery's Constant for N2 at 300 K are in "DAC_data/Results/".
The results of the GCMC calculations for the Henery's Constant for CO2 at 350 K are in "DAC_data/CSD_FEASST_Materials/Results/".
The results of the GCMC calculations for equilibrium uptake at 101325 Pa of N2 at 300 K are in "DAC_data/Atmosphere_check/".
The results of the GCMC calculations for saturation uptake of CO2 at 200 K are in "DAC_data/Saturation/".


Specific Heat Capacity Predictions:
The results of the CV predictions are in "DAC_data/CV_predictions/"

Intrinsic DAC Calculation Results:
The results of the Intrinsic DAC calculations using a path that first heats from 250 K to 375 K, then pulls vacuum from 101325 Pa to  42844.839679358716 Pa are in "DAC_data/SinglePath_Intrinsic_Cycle/"
The results of the Intrinsic DAC calculations after finding Pareto optimal paths for CO2 capture efficiency and captured CO2 purity are in "DAC_data/Optimized_Intrinsic_Cycle/"

----Further Details----

In "DAC_data/Results/":
"beta" is the inverse temperature (1/(kB*NA*T), where kB is the Boltzmann's constant and NA is Avogadro's Number) in units of mol/kJ.
"Kcoeff" are the Henry's constant coefficients in units of mmol/(kg Pa) - per kilogram of sorbent basis. 
 
In "DAC_data/CSD_FEASST_Materials/Results/":
"beta" is the inverse temperature (1/(kB*NA*T), where kB is the Boltzmann's constant and NA is Avogadro's Number) in units of mol/kJ.
"Kcoeff" are the Henry's constant coefficients in units of mmol/(kg Pa) - per kilogram of sorbent basis. 

In "DAC_data/CSD_FEASST_Materials/Atmosphere_check/":
"beta" is the inverse temperature (1/(kB*NA*T), where kB is the Boltzmann's constant and NA is Avogadro's Number) in units of mol/kJ.
"temperature" is the  temperature ((kB*NA*T), where kB is the Boltzmann's constant and NA is Avogadro's Number) in units of kJ/mol.
"target_p" is the target pressure ((P * NA), where NA is Avogadro's Number) in units of kJ/(mol Å^3). 
"betamu" is log(x * P/T) where x is the mole fraction of the gas, P is the target total pressure, and T is the temperature.

In "DAC_data/CSD_FEASST_Materials/Saturation/":
"temperature" is the  temperature ((kB*NA*T), where kB is the Boltzmann's constant and NA is Avogadro's Number) in units of kJ/mol.
"cutoff" is a cutoff radius in Å. 
"mu" is (log(beta * fugacity)/beta).
"loading" is the average number of adsorbed molecules.


