from Helpers import container, conditionally_defined
from State import state

import numpy as np


@container
class Phasor_Interface_Methods:
	def construct_wave(angular_freq, phase_angle, amplitude):
		return np.array((angular_freq, phase_angle, amplitude))

	def valid_angular_frequency(waves):
		return len(waves) > 1

	def update_angular_frequency(x, phase_angle):

		return 2 * np.pi / (x - phase_angle)

	def update_angular_phase_angle(x, phase_angle):

		return x - phase_angle

	def get_current_likelihood(x, Likelihood, phase_angle):
		return Likelihood[x - phase_angle]

	def get_current_coherence(x, Coherence, phase_angle):

		return Coherence[x - phase_angle]

	def construct_waves(wave, waves):
		return np.concat([waves, [wave]])

	def get_Likelihood(model_statistics):
		return model_statistics[0]

	def get_Coherence(model_statistics):
		return model_statistics[1]


@container
class PhasorStatistics:

	def processWaves(waves):
		return waves[2:]

	def phasorValues(waves):
		omega = waves[:, 0]
		T = waves[:, 1]	# phase angle defined from common start referene t=0
		amplitude = np.ones_like(T) if waves.shape[-1] == 2 else waves[:, 2]
		t = T[-1]

		phi = t - T
		return omega, phi, amplitude

	def calculateHorizon(horizon, phi):
		if phi.shape[0] > 2:
			return horizon
		if phi.shape[0] > 6:
			d = np.diff(phi)
			statistic = max(d)
		else:
			statistic = np.mean(phi)

		if 3 * statistic > horizon:
			return int(2 * statistic)	# just to be save
		return horizon

	def getPhasors(amplitude, envelope, omega):
		return amplitude * np.exp(-envelope) * np.exp(1j * omega)

	def phasorStatistics(phasor):

		s_sum = np.sum(phasor, axis=1)
		m_sum = np.abs(phasor).sum(axis=1)
		psi = s_sum / m_sum
		coherence = np.abs(psi)
		return psi, coherence

	def getLikelihood(psi, coherence, mode="normalised", func=None, **kwargs):
		if mode == "normalised":
			return (coherence + psi.real) / 2
		if mode == "max":
			return np.maximum(0, psi.real)
		if func is not None:
			return func(psi, coherence, **kwargs)
		raise ValueError(f"{mode} is not defined")

	def predictPhasorAverage(
		waves,
		*,
		horizon=2000,
		amplitudeFunc=None,
		envelopeFunc=None,
		omegaFunc=None,
		**kwargs,
	):
		"""
		waves=[(angular_freq,phase_angle_k,amplitude),...]
		"""
		waves = PhasorStatistics.processWaves(waves)

		if len(waves) == 0:
			return np.zeros(horizon), np.zeros(horizon)

		omega, phi, amplitude = PhasorStatistics.phasorValues(waves)
		horizon = PhasorStatistics.calculateHorizon(horizon, phi)

		Delta_t = np.arange(0, horizon + 1)[:, None]

		@conditionally_defined(amplitudeFunc, **kwargs)
		def amplitudeFunc(amplitude, **kwargs):
			return np.ones_like(amplitude)

		@conditionally_defined(envelopeFunc, **kwargs)
		def envelopeFunc(phi, **kwargs):
			return np.zeros_like(phi)

		@conditionally_defined(omegaFunc, **kwargs)
		def omegaFunc(omega, phi, **kwargs):
			return phi * omega

		Envelope_t = envelopeFunc(phi)
		Omega_t = omegaFunc(omega, phi)
		Amplitude_t = amplitudeFunc(amplitude)

		Envelope_rot = envelopeFunc(Delta_t, **kwargs)
		Omega_rot = omegaFunc(omega, Delta_t, **kwargs)
		Amplitude_rot = np.ones_like(Delta_t, **kwargs)

		x_now = PhasorStatistics.getPhasors(Amplitude_t, Envelope_t, Omega_t)
		x_rot = PhasorStatistics.getPhasors(Amplitude_rot, Envelope_rot, Omega_rot)
		x_project = x_rot * x_now

		psi, coherence = PhasorStatistics.phasorStatistics(x_project)
		likelihood = PhasorStatistics.getLikelihood(**locals())

		return [likelihood, coherence]


@state
class Phasor_State:
	horizon = 1000

	Likelihood = [0] * horizon
	Coherence = [0] * horizon
	waves = np.empty((0, 3), dtype=float)
	likelihood = 0
	angular_freq = np.nan
	buffer = [None]
	phase_angle = 0
	amplitudeFunc = None
	envelopeFunc = None
	omegaFunc = None
	model_statistics = None

	__TICK__ = {
		"update": {
			"angular_freq": {
				"rule": Phasor_Interface_Methods.update_angular_frequency,
				"condition": Phasor_Interface_Methods.valid_angular_frequency,
			}
		},
		"return": {
			"current_likelihood": {"rule": Phasor_Interface_Methods.get_current_coherence},
			"current_coherence": {"rule": Phasor_Interface_Methods.get_current_likelihood},
		},
	}

	__EVENT__ = {
		"update": {
			"phase_angle": {
				"value": "x",
			},
			"amplitude": {"value": "trigger"},
			"wave": {"rule": Phasor_Interface_Methods.construct_wave},
			"waves": {"rule": Phasor_Interface_Methods.construct_waves},
			"model_statistics": {"rule": PhasorStatistics.predictPhasorAverage},
			"Likelihood": {"rule": Phasor_Interface_Methods.get_Likelihood},
			"Coherence": {
				"rule": Phasor_Interface_Methods.get_Coherence,
			},
		},
		"return": {
			"Likelihood": {"value": "Likelihood"},
			"Coherence": {"value": "Coherence"},
		},
	}


fire = False
y_agg = []
diff_gg = []
l_agg = []

u_agg = []
f_agg = []

data = np.load("20_percent_30_perncent_1101.npz")
x = data["x"]
y = data["y"]
