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

| Symbol | Literatur | Characterisation | Interpretation |
| :----- | :-------- | :--------------- | :------------- |
| $P_{\max}$ | `sys` | Global maximum ('peak') of $P$ (occurs at $t=0$ and $t=T$) | High point of RV-systolic phase |
| $P_{\text{es}}$ | `esp` | (1st) Local minimum of $P^{\prime\prime}$ | End of systolic phase. Just before closure of pulmonary valve. |
| $P_{\text{anti-epad}}$ | `anti-epad` | Local (and absolute) minimum of $P^{\prime}$ | End of estimated pulmonary artery diastolic phase. Onset of isovolumetric relaxation phase. |
| $P_{\text{sd}}$ | `sdp` | (1st) Local maximum of $P^{\prime\prime}$ | Start of diastolic phase. Just before opening of tricuspid valve. |
| $P_{\min}$ | `dia` | Global minimum of $P$ | First low point of RV diastolic phase. |
| — | — | Local minimum of $P^{\prime\prime}$ | |
| $P_{\text{ed}}$ | `edp` | (2nd) Local maximum of $P^{\prime\prime}$ | End of diastolic phase. End of RV diastolic phase. |
| $P_{\text{epad}}$ | `epad` | Local (and absolute) maximum of $P^{\prime}$ | Start of estimated pulmonary artery diastolic phase. Coincidence of RV- and pulmonary arterial pressure. |
| $P_{\text{bs}}$ | `bsp` / `eivc` | (2nd) Local minimum of $P^{\prime\prime}$ | Start (begin) of systolic phase. End of iso-volumetric contractions, pulmonary valve is opened. |

These points define important phases of the cardiovascular cycle:

| from  | (via) | to    | Name | Interpretation |
| :---: | :---: | :---: | :--- | :------------- |
| `bs(p)` | `sys` | `es(p)` | Systolic phase | High pressure, ejection. |
| `es(p)` | `anti-epad` | `sd(p)` | Iso-volumetric relaxation (IVR) | Pressure reduction whilst no/negligible change in volume. |
| `sd(p)` | `dia` | `ed(p)` | Diastolic phase | Low pressure, filling. |
| `ed(p)` | `epad` | `bs(p)` | Iso-volumetric contraction (IVC) | Pressure increase whilst no/negligible change in volume. |

## Definition of special points for $V(t)$ ##

Consider cycles in peak-to-peak format
Assume without loss of generality
that this is defined on a time interval $[0, T]$.
The following points are listed out in chronological order
("modulo" the peak) within such a cycle:

| Symbol | Literature | Characterisation | Interpretation |
| :----- | :--------- | :--------------- | :------------- |
| $V_{\max}$ | — | Global maximum ('peak') of $V$ (occurs at $t=0$ and $t=T$) | |
| — | — | (1st) Local minimum of $V^{\prime\prime}$ | |
| $V_{\text{bs}}$ | **`bsv`** | Local (and absolute) minimum of $V^{\prime}$ | |
| $V_{\text{es}}$ | **`esv`** | (1st) Local maximum of $V^{\prime\prime}$ | |
| $V_{\min}$ | — | Global minimum of $V$ | |
| — | — | Local minimum of $V^{\prime\prime}$ | |
| $V_{\text{bd}}$ | **`bdv`** | (2nd) Local maximum of $V^{\prime\prime}$ | |
| $V_{\text{ed}}$ | **`edv`** | Local (and absolute) maximum of $V^{\prime}$ | |
| — | — | (2nd) Local minimum of $V^{\prime\prime}$ | |

## Combined analysis ##

- Using the above definitions,
  the time-series are matched by forcing `edp` = `edv`.
- Once matched one can then compute

  - `P_max` by fitting a sin-curve to the isometric phase of the pressure curve.
  - `sv` (stroke volume) `:= edv - esv`
  - `ees :=  (P_max − esp)/sv`
  - `ea := esp / sv`

[^Gaertner2023PaperBeat]: Gaertner, M., Glocker, R., Glocker, F., & Hopf, H. (2023). _Pressure‐based beat‐to‐beat right ventricular ejection fraction and Tau from continuous measured ventricular pressures in COVID‐19 ARDS patients_. In Pulmonary Circulation (Vol. 13, Issue 1). Wiley. https://doi.org/10.1002/pul2.12179

[^Vanderpool2020PaperSurfing]: Vanderpool, R. R., Puri, R., Osorio, A., Wickstrom, K., Desai, A. A., Black, S. M., Garcia, J. G. N., Yuan, J. X. ‐J., & Rischard, F. P. (2020). _Surfing the right ventricular pressure waveform: methods to assess global, systolic and diastolic RV function from a clinical right heart catheterization_. In Pulmonary Circulation (Vol. 10, Issue 1, pp. 1–11). Wiley. https://doi.org/10.1177/2045894019850993
