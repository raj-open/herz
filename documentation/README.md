# Notes on computations #

Here we document technical definitions and (some) methods.

## Definition of special points for $P(t)$ ##

For these definitions, we rely on [Gaertner, et al.][^Gaertner2023PaperBeat] and [Vanderpool, et al., Fig. 1, p. 3][^Vanderpool2020PaperSurfing].

The following is an equivalent reformulation of the definitions in [Gaertner, et al., Fig. 1, p. 3][^Gaertner2023PaperBeat].

1. Prepare the pressure time-series $P(t)$ in such a way,
   that the cycles are defined from peak-to-peak.
2. Consider one such cycle.
   Assume without loss of generality
   that this is defined on a time interval $[0,\:T]$

The following points are listed out in chronological within such a cycle:

| Symbol | Characterisation | Interpretation |
| :----- | :--------------- | :------------- |
| **`esp`** | 1st local minimum of $P^{\prime\prime}$ | Just before closure of pulmonary valve |
| **`anti-epad`** | 1st local (and absolut) minimum of $P^{\prime}$ | onset of isovolumetric relaxation phase |
| **`sdp`** | 1st local maximum of $P^{\prime\prime}$ after `anti-epad` | Start of diastolic phase. Just before opening of tricuspid valve. |
| **`dia`** | First local minimum of $P$ after `anti-epad` (and `sdp`) | Low point of RV diastolic phase |
| **`edp`** | 2nd local (and absolute) maximum of $P^{\prime\prime}$ after `anti-epad` (and `dia`) | End of RV diastolic phase |
| **`epad`** | 2nd local (and absolute) maximum of $P^{\prime}$ | Coincidence of RV- and pulmonary arterial pressure |
| **`eivc`** | First local minimum of $P^{\prime\prime}$ after `epad` | End of isovolumentric contractions, pulmonary valve is opened. |
| **`sys`** | Local maximum of $P$ after `epad`. Also: global maximum ('peaks') of $P$, occurs at $t=0$ and $t=T$. | High point of RV-systolic phase |

## Definition of special points for $V(t)$ ##

(_Under construction_)

[^Gaertner2023PaperBeat]: Gaertner, M., Glocker, R., Glocker, F., & Hopf, H. (2023). _Pressure‐based beat‐to‐beat right ventricular ejection fraction and Tau from continuous measured ventricular pressures in COVID‐19 ARDS patients_. In Pulmonary Circulation (Vol. 13, Issue 1). Wiley. https://doi.org/10.1002/pul2.12179

[^Vanderpool2020PaperSurfing]: Vanderpool, R. R., Puri, R., Osorio, A., Wickstrom, K., Desai, A. A., Black, S. M., Garcia, J. G. N., Yuan, J. X. ‐J., & Rischard, F. P. (2020). _Surfing the right ventricular pressure waveform: methods to assess global, systolic and diastolic RV function from a clinical right heart catheterization_. In Pulmonary Circulation (Vol. 10, Issue 1, pp. 1–11). Wiley. https://doi.org/10.1177/2045894019850993
