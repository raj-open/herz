# Notes on computations #

Here we document technical definitions and (some) methods
for analysing right ventricular (RV)
pressure and volume data.

- We obtain time-series data as follows:
  - Pressure $\{(t_{i},P(t_{i}))\}_{i}$ from pressure wire measurements (alternative via EKG).
  - Volume $\{(t_{j},V(t_{j}))\}_{j}$ from MRT-scans (alternative via CT-scans).
- Portions of the data of different cycle-length are
  treated as artefacts (or they contain extra systoles)
  and as such removed.
- The cycles are formatted in peak-to-peak form and normalised
  (removal of linear-drift and rescaled to ensure L²-norm of $1$),
  so that the cycles can be comparably treated.
- For each time-series, a single curve (polynomial)
  is simultaneously fitted to all cycles.
  Since we use L²-minimisation (involves use of orthonormal bases),
  this is equivalent to fitting to the 'average' of all cycles.

## Definition of special points for $P(t)$ ##

For these definitions, we rely on [Gaertner, et al.][^Gaertner2023PaperBeat] and [Vanderpool, et al., Fig. 1, p. 3][^Vanderpool2020PaperSurfing].
The following is an equivalent reformulation of the definitions in [Gaertner, et al., Fig. 1, p. 3][^Gaertner2023PaperBeat].

Consider cycles in peak-to-peak format
Assume without loss of generality
that this is defined on a time interval $[0, T]$.
The following points are listed out in chronological order
("modulo" the peak) within such a cycle:

| Symbol | Characterisation | Interpretation |
| :----- | :--------------- | :------------- |
| **`sys`** | Global maximum ('peak') of $P$. Occurs at $t=0$ and $t=T$. | High point of RV-systolic phase |
| **`esp`** | (1st) Local minimum of $P^{\prime\prime}$. | Just before closure of pulmonary valve. |
| **`anti-epad`** | Local (and absolute) minimum of $P^{\prime}$. | Onset of isovolumetric relaxation phase. |
| **`sdp`** | (1st) Local maximum of $P^{\prime\prime}$. | Start of diastolic phase. Just before opening of tricuspid valve. |
| **`dia`** | Local minimum of $P$. | First low point of RV diastolic phase. |
| **`edp`** | (2nd) Local maximum of $P^{\prime\prime}$. | End of RV diastolic phase. |
| **`epad`** | Local (and absolute) maximum of $P^{\prime}$. | Coincidence of RV- and pulmonary arterial pressure. |
| **`bsp`** / **`eivc`** | (2nd) Local minimum of $P^{\prime\prime}$. | End of iso-volumetric contractions, pulmonary valve is opened. |

## Definition of special points for $V(t)$ ##

Consider cycles in peak-to-peak format
Assume without loss of generality
that this is defined on a time interval $[0, T]$.
The following points are listed out in chronological order
("modulo" the peak) within such a cycle:

| Symbol | Characterisation | Interpretation |
| :----- | :--------------- | :------------- |
| $V_{\max}$ | Global maximum ('peak') of $V$. Occurs at $t=0$ and $t=T$. | |
| **`anti-evad`** | Local (and absolute) minimum of $V^{\prime}$. | |
| **`sdv`** | Local maximum of $V^{\prime\prime}$. | |
| $V_{\min}$ | Global maximum ('peak') of $V$. Occurs at $t=0$ and $t=T$. | |
| **`???`** | Local minimum of $V^{\prime\prime}$. | |
| **`edv`** | (2nd) Local maximum of $V^{\prime\prime}$. | |
| **`evad`** | Local (and absolute) maximum of $V^{\prime}$. | |

## Combined analysis ##

- Using the above definitions,
  the time-series are matched by forcing `edp` = `edv`.
- Once matched one can then compute

  - `P_max` by fitting a sin-curve to the isometric phase of the pressure curve.
  - `ees := P_max - esp · edv - esv`
  - `ea := esp / sv`

[^Gaertner2023PaperBeat]: Gaertner, M., Glocker, R., Glocker, F., & Hopf, H. (2023). _Pressure‐based beat‐to‐beat right ventricular ejection fraction and Tau from continuous measured ventricular pressures in COVID‐19 ARDS patients_. In Pulmonary Circulation (Vol. 13, Issue 1). Wiley. https://doi.org/10.1002/pul2.12179

[^Vanderpool2020PaperSurfing]: Vanderpool, R. R., Puri, R., Osorio, A., Wickstrom, K., Desai, A. A., Black, S. M., Garcia, J. G. N., Yuan, J. X. ‐J., & Rischard, F. P. (2020). _Surfing the right ventricular pressure waveform: methods to assess global, systolic and diastolic RV function from a clinical right heart catheterization_. In Pulmonary Circulation (Vol. 10, Issue 1, pp. 1–11). Wiley. https://doi.org/10.1177/2045894019850993
