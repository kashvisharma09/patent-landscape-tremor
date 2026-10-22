# Draft patent specification (practice document)

> **Status: practice draft, not a filed application and not legal advice.**
> It is written only from the device description in `config.py`. Every item marked
> **[CONFIRM]** is a placeholder: replace it with the real value from your device before
> using this anywhere. Differences from the closest prior art must come from your own
> reading of the full claims of the patents found by `python -m src.run_prior_art`.

## Title

Wearable closed-loop system for detecting and suppressing pathological hand tremor

## Technical field

The invention relates to wearable medical devices, and more particularly to a wrist-worn
device that senses tremor with an inertial measurement unit and suppresses it by applying
a counter-phase mechanical motion.

## Background

Tremor, such as essential tremor and Parkinson's tremor, is an involuntary oscillation of a
body part, typically at a frequency of about 4 to 12 Hz. It makes everyday tasks such as eating,
writing and drinking difficult. Known approaches include drug treatment, implanted or
surface electrical stimulation, hand-held stabilising utensils, and passive weights.
These approaches may be invasive, bulky, task-specific or not adaptive to the individual user.
**[CONFIRM: add 2 to 3 specific limitations of the closest prior-art patents found in
`reports/prior_art_top10.csv`, citing their numbers.]**

## Summary

A wearable device comprises: a housing configured to be worn on a wrist; an inertial
measurement unit (IMU) having at least six measurement axes; a microcontroller; and an
actuator. The microcontroller receives IMU data, applies a transform and digital filtering to
isolate a tremor component in a band of about 4 to 12 Hz, and drives the actuator to apply
motion in counter-phase to the isolated tremor component, thereby reducing tremor amplitude.
In some embodiments an adaptive machine-learning classifier distinguishes tremor from
voluntary movement and personalises the filter and actuation parameters to the user, so that
voluntary motion is not suppressed.

## Brief description of the drawings

- FIG. 1: wrist-worn device on a user's arm. **[CONFIRM: prepare drawing]**
- FIG. 2: block diagram of the IMU, microcontroller, actuator driver and actuator.
- FIG. 3: flowchart of the sensing, filtering and counter-phase actuation loop.
- FIG. 4: example of an input tremor signal, the isolated tremor component and the
  counter-phase actuation signal.

## Detailed description

### Hardware

The device 100 includes a housing 110 attached to the wrist by a strap. Inside the housing are
an IMU 120 (six-axis: three-axis accelerometer and three-axis gyroscope), a microcontroller
130, an actuator driver 140 and an actuator 150. In one embodiment the actuator 150 is a
servo motor driven by pulse-width modulation (PWM) from the driver 140. **[CONFIRM: IMU model,
sampling rate, microcontroller model, actuator type and stroke, battery, housing materials.]**

### Operation

1. The IMU 120 samples motion at a rate high enough to resolve the tremor band
   **[CONFIRM: sampling rate in Hz]**.
2. The microcontroller 130 buffers samples in a window and computes a fast Fourier transform (FFT)
   to find the dominant frequency in the band of about 4 to 12 Hz.
3. A digital band-pass filter centred on the dominant frequency isolates the tremor component
   from slower voluntary motion and from higher-frequency noise.
4. The microcontroller generates a drive signal with a phase opposite to that of the isolated
   tremor component and outputs it as a PWM command to the actuator driver 140.
5. The actuator 150 applies a counter motion at the wrist, reducing the tremor amplitude.
6. The IMU continues to measure the residual motion, closing the loop; the amplitude and phase
   of the drive signal are adjusted to minimise the residual tremor.

### Adaptive classification

A machine-learning classifier executed on the microcontroller (or on a paired device) receives
features of the IMU data, such as band power, dominant frequency and amplitude, and classifies
each window as tremor or voluntary movement. Actuation is applied only when the window is
classified as tremor. Classifier parameters or filter parameters are updated using the user's own
data to personalise operation **[CONFIRM: model type, training method, latency measured]**.

### Alternative embodiments

The actuator may be a vibration motor, a linear actuator or a gyroscopic element. The IMU may
be placed on the hand, forearm or finger. Processing may be split between the wearable device and
a smartphone. **[CONFIRM which alternatives you actually want to claim or disclose.]**

## Claims (draft)

1. A wearable tremor suppression device, comprising:
   a housing configured to be worn on a wrist of a user;
   an inertial measurement unit in the housing and configured to output motion data;
   an actuator coupled to the housing; and
   a microcontroller configured to: (a) isolate, from the motion data, a tremor component in a
   frequency band of about 4 Hz to about 12 Hz using a frequency transform and a digital filter;
   and (b) drive the actuator to apply motion in counter-phase to the tremor component.
2. The device of claim 1, wherein the inertial measurement unit has at least six axes,
   comprising a three-axis accelerometer and a three-axis gyroscope.
3. The device of claim 1, wherein the frequency transform is a fast Fourier transform.
4. The device of claim 1, wherein the actuator is a servo motor driven by a pulse-width-modulated
   signal from the microcontroller.
5. The device of claim 1, wherein the microcontroller is further configured to measure residual
   tremor in the motion data after actuation and adjust an amplitude or a phase of the counter-phase
   motion to reduce the residual tremor (closed-loop operation).
6. The device of claim 1, further comprising a classifier configured to classify the motion data as
   tremor or voluntary movement, wherein the microcontroller drives the actuator only when the
   motion data is classified as tremor.
7. The device of claim 6, wherein the classifier is a machine-learning classifier whose parameters
   are adapted to the user from the user's own motion data.
8. A method of suppressing tremor, comprising: sensing wrist motion with an inertial measurement
   unit; isolating a tremor component in a band of about 4 Hz to about 12 Hz using a frequency
   transform and a digital filter; and driving an actuator worn on the wrist to apply motion in
   counter-phase to the tremor component.

**[CONFIRM: claims must be checked against the claims of the closest prior art. Claim 1 is likely
broad; the dependent claims show where narrower fall-back positions could be.]**

## Abstract

A wrist-worn device suppresses pathological tremor. An inertial measurement unit senses wrist
motion. A microcontroller isolates a tremor component in a band of about 4 to 12 Hz using a
frequency transform and digital filtering, and drives an actuator to apply motion in counter-phase
to the isolated component, reducing tremor. A classifier may distinguish tremor from voluntary
movement, and parameters may be adapted to the user.
