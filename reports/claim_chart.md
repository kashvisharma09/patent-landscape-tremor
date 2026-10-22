# Abstract-level claim chart: my device vs closest prior art

**My device:** A wrist-worn closed-loop device using a 6-axis inertial measurement unit to capture tremor oscillations at 4 to 12 Hz, a microcontroller applying FFT and digital filtering to isolate the tremor signal, and a servo actuator driven by PWM to apply counter-phase motion for suppression, with an adaptive machine learning classifier for low-latency personalization.

> Screening only. "Yes" means the abstract mentions the feature; it does not mean a claim covers it. Read the full claims of each patent before drawing conclusions.

| # | Patent | Priority | Assignee | Similarity | Title |
|---|---|---|---|---|---|
| 1 | [US12415076B1](https://patents.google.com/patent/US12415076B1) | 2021-07-13 | LEMOYNE ROBERT | MASTROIANNI TIMOTHY | 0.10 | Multidisciplinary design optimization of neuromodulation systems |
| 2 | [CN101612043B](https://patents.google.com/patent/CN101612043B) | 2009-08-04 | HEFEI INST PHYSICAL SCI CAS | 0.09 | Wearable robot for detecting and suppressing tremor of human arms and  |
| 3 | [CN115500822B](https://patents.google.com/patent/CN115500822B) | 2022-10-21 | nan | 0.09 | Parkinson detection system and equipment based on wrist tremor signal |

| Element of my device | #1 | #2 | #3 |
|---|---|---|---|
| Wrist-worn / wearable form factor | Yes (wearable) | Yes (wearable) | Yes (wrist) |
| Inertial sensing (IMU / accelerometer / gyroscope) | Yes (inertial) | Yes (imu) | No |
| Tremor detection in a frequency band (about 4-12 Hz) | No | No | No |
| Digital signal processing (FFT / filtering) | No | Yes (filter) | No |
| Microcontroller / processor | No | No | No |
| Actuator applying counter-phase / opposing motion | No | Yes (suppress) | No |
| Closed-loop feedback | Yes (closed loop) | Yes (closed loop) | No |
| Machine-learning / adaptive personalisation | Yes (machine learning) | Yes (adaptive) | Yes (machine learning) |

**Elements found in abstract:** #1 US12415076B1: 4/8, #2 CN101612043B: 6/8, #3 CN115500822B: 2/8

**Where my device may differ:** elements marked "No" across all columns are candidates for what is distinctive. Confirm by reading the full text, then write the differences into the draft specification and claims.
