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

## The defining phases — systole and diastole ##

Consider the system of the right ventricle (right heart chamber).

- In its ordinary mode, the behaviour of this system is assumed to consist of periodic cycles.
- These cycles may be (slightly) time-dilated or scaled (quantities such as volume, pressure).
- In real data, these cycles may be interspersed by shorter cycles or pauses.
  These are attributed to a different mode of the system and thus filtered out.
- The cycles consist of 2 phases (and transitions between these):

  - the **systolic phase**
  - the **diastolic phase**

  For each of these phases we study **3 critical points**: begin/start, main, end.
  These demarcate the (disjoint) time-intervals designated to these two phases.

  | Phase   | Part | Symbol | Characterisation |
  | :-----: | :--- | :----- | :--------------- |
  | Systole | — | — | Contraction phase. |
  | " | begin | `bs` | $P^{\prime\prime}$ and $V^{\prime\prime}$ are local minima |
  | " | main | `sys` | $P$ is maximal and $V^{\prime}$ (i.e. flow) minimal |
  | " | end | `es` | $P^{\prime\prime}$ is a local minimum and $V^{\prime\prime}$ a local maximum |
  | Diastole | — | — | Relaxation phase. |
  | " | begin | `bd` | $P^{\prime\prime}$ and $V^{\prime\prime}$ are local maxima |
  | " | main | `dia` | $P$ is minimal and $V^{\prime}$ (i.e. flow) maximal |
  | " | end | `ed` | $P^{\prime\prime}$ is a local maximum and $V^{\prime\prime}$ a local minimum |

  Alongside RV pressure/volume measurements, it is of interest to consider the pulmonary artery.
  There is a certain point at which RV-pressure provides an estimate for pulmonary arterial pressure.
  This point and a corresponding point demarcate the start and end of the pulmonary arterial diastole
  and occur between the above two phases:

  | Name | Between     | Symbol | Characterisation |
  | :----- | :---------- | :----- | :--------------- |
  | Est. pulm. art. diastole | `ed` — `bs` | `epad` | Rate of change of $P$ maximal |
  | End of `epad` | `es` — `bd` | `anti-epad` | Rate of change of $P$ minimal |

To fit these assumptions we use polynomials of a sufficiently high degree,
to allow for enough critical points which correspond to these points of interest.
This requires some pre- and post-processing.

Note that for alignment purposes, it is most reliable to match points defined by the lowest
possible derivative orders.
And since we can more reliably recognise maximal pressure values over minima,
we judge that the best candidate for matching be `sys` ($P$ maximal, $V^{\prime}$ minimal).

## Definition of special points for $P(t)$ ##

For these definitions, we rely on [Gaertner, et al.][^Gaertner2023PaperBeat] and [Vanderpool, et al., Fig. 1, p. 3][^Vanderpool2020PaperSurfing].
The following is an equivalent reformulation of the definitions in [Gaertner, et al., Fig. 1, p. 3][^Gaertner2023PaperBeat].

Consider cycles in peak-to-peak format
Assume without loss of generality
that this is defined on a time interval $[0, T]$.
The following points are listed out in chronological order
("modulo" the peak) within such a cycle:

| Symbol | Literatur | Characterisation | Further comments |
| :----- | :-------- | :--------------- | :------------- |
| $P_{\max}$ | `sys` | Global maximum ('peak') of $P$ | Directly recognisable, occurs @ $t \in \{0,T\}$. |
| $P_{\text{es}}$ | `esp` | (1st) Local minimum of $P^{\prime\prime}$ | Just before closure of pulmonary valve. |
| $P_{\text{anti-epad}}$ | `anti-epad` | Local (and absolute) minimum of $P^{\prime}$ | Onset of iso-volumetric relaxation phase. |
| $P_{\text{bd}}$ | `bdp` | (1st) Local maximum of $P^{\prime\prime}$ | Just before opening of tricuspid valve. |
| $P_{\min}$ | `dia` | Global minimum of $P$ | First low point of RV diastolic phase. |
| — | — | Local minimum of $P^{\prime\prime}$ | |
| $P_{\text{ed}}$ | `edp` | (2nd) Local maximum of $P^{\prime\prime}$ | |
| $P_{\text{epad}}$ | `epad` | Local (and absolute) maximum of $P^{\prime}$ | Start of estimated pulmonary artery diastolic phase. Coincidence of RV- and pulmonary arterial pressure. |
| $P_{\text{bs}}$ | `bsp` / `eivc` | (2nd) Local minimum of $P^{\prime\prime}$ | End of iso-volumetric contractions, pulmonary valve is opened. |

## Definition of special points for $V(t)$ ##

Consider cycles in peak-to-peak format
Assume without loss of generality
that this is defined on a time interval $[0, T]$.
The following points are listed out in chronological order
("modulo" the peak) within such a cycle:

| Symbol | Literature | Characterisation |
| :----- | :--------- | :--------------- |
| $V_{\max}$ | — | Global maximum ('peak') of $V$ (occurs @ $t \in \{0,T\}$). |
| $V_{\text{bs}}$ | `bsv` | (1st) Local minimum of $V^{\prime\prime}$ |
| $V_{\text{sys}}$ | `sv` | Local (and absolute) minimum of $V^{\prime}$ |
| $V_{\text{es}}$ | `esv` | (1st) Local maximum of $V^{\prime\prime}$ |
| $V_{\min}$ | — | Global minimum of $V$ |
| — | — | (2nd) Local minimum of $V^{\prime\prime}$ |
| $V_{\text{bd}}$ | `bdv` | (2nd) Local maximum of $V^{\prime\prime}$ |
| $V_{\text{dia}}$ | `dv` | Local (and absolute) maximum of $V^{\prime}$ |
| $V_{\text{ed}}$ | `edv` | (3rd) Local minimum of $V^{\prime\prime}$ |

## Further analysis ##

Once the two series are matched, we perform post-processing:

1. The pressure-curve appears to be in form of a sinusoidal curve between `epad` and `anti-epad`,
   and constant or with at most a linear drift between `sd` and `ed`.
   This behaviour owes to the changes in volume.

   Under iso-volumetric conditions, the pressure curve could be approximate by a sinusoid, with a higher peak.
   We can recover this behaviour by fitting such a curve to the parts of the data
   between `es` – `bd` and `ed` — `bs`
   (i.e. the approximate iso-volumetric phases).
   The amplitude of this approximation is denoted $P^{\text{iso}}_{\max}$.


2. Due to physical limitations, it is difficult to perform volume measure
   whilst volume is maximal and flow is at $0~\text{mL/s}$.
   For this reason, the peak-to-peak instrument measurements of volume
   is stopped upon the 2nd maximum.
   We can therefore assume that there is an unmeasured (short) stretch
   of time, wherein the volume remains constant (maximal)
   and flow remains $0~\text{mL/s}$.

   Indeed, it appears that our volume cycles are always $O(10~\text{ms})$
   shorter than pressure cycles.
   We can thus reasonably extend the volume cycles,
   noting in particular that this will not affect our matching schema
   ($V^{\prime}$ min, $P$ max).

3. The diastolic phase (`bd` — `ed`) can be modelled
   by an exponential relation—**EDPVR**, or **end diastolic presssure-volume relation**,
   which is given as follows:

   $P(V) = \alpha(e^{\beta V} - 1)$

   where $\alpha,\beta \in (0,\:\infty)$.

Once these these have been adjusted, we may compute

| Name | Symbol | Definition |
| :--- | :----- | :--------- |
| End systolic elastance | `ees` | $\text{ees} \coloneqq \frac{P^{\text{iso}}_{\max} − P_{\text{es}}}{V_{\text{ed}} - V_{\text{es}}}$ |
| Arterial elastance | `ea` | $\text{ea} \coloneqq \frac{P_{\text{es}}}{V_{\text{ed}} - V_{\text{es}}}$ |
| End diastolic elastance | `eed` | $\text{eed} \coloneqq \tfrac{dP}{dV}\mid_{\text{edp}} = \alpha \beta e^{\beta V_{\text{ed}}} = \beta \cdot (P_{\text{ed}} + \alpha)$ |

[^Gaertner2023PaperBeat]: Gaertner, M., Glocker, R., Glocker, F., & Hopf, H. (2023). _Pressure‐based beat‐to‐beat right ventricular ejection fraction and Tau from continuous measured ventricular pressures in COVID‐19 ARDS patients_. In Pulmonary Circulation (Vol. 13, Issue 1). Wiley. https://doi.org/10.1002/pul2.12179

[^Vanderpool2020PaperSurfing]: Vanderpool, R. R., Puri, R., Osorio, A., Wickstrom, K., Desai, A. A., Black, S. M., Garcia, J. G. N., Yuan, J. X. ‐J., & Rischard, F. P. (2020). _Surfing the right ventricular pressure waveform: methods to assess global, systolic and diastolic RV function from a clinical right heart catheterization_. In Pulmonary Circulation (Vol. 10, Issue 1, pp. 1–11). Wiley. https://doi.org/10.1177/2045894019850993
