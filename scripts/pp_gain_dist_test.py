from dataset import covid_timeseries_dataset
import tensorflow_probability as tfp
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

df = covid_timeseries_dataset.load_latest()

confirmed_gain = None
dates = None

# just find Czechia country
# FIXME: fix code, it's ugly
for index, row in df.iterrows():
    country, timeline = row

    if country != "Czechia":
        continue

#     confirmed_gain = timeline["confirmed_gain"]
    confirmed_gain = np.trim_zeros(timeline["confirmed_gain"], "f")
    dates = timeline.index[-len(confirmed_gain):]

    break

print(confirmed_gain)
print(dates)

t_confirmed_gain = tf.convert_to_tensor(confirmed_gain, dtype=tf.float32)
t_dates = tf.convert_to_tensor(np.arange(0, len(dates)), dtype=tf.int32)
tf.print("before size")
# t_size = tf.constant(len(dates))
tf.print("after size")


def joint_log_prob(lambda_1, lambda_2, tau):
    rv_lambda_1 = tfp.distributions.Normal(loc=0., scale=1000.)
    rv_lambda_2 = tfp.distributions.Normal(loc=0., scale=1000.)

    rv_tau = tfp.distributions.Uniform(low=0, high=len(dates))

    indices = tf.cast(tau * tf.cast(len(dates), dtype=tf.float32) <=
                      tf.cast(tf.range(len(dates)), dtype=tf.float32), dtype=tf.int32)

    lambda_prime = tf.gather([lambda_1, lambda_2], indices=indices)
    rv_observation = tfp.distributions.Poisson(rate=lambda_prime)

    return (
        rv_lambda_1.log_prob(lambda_1)
        + rv_lambda_2.log_prob(lambda_2)
        + rv_tau.log_prob(tau)
        + tf.reduce_sum(rv_observation.log_prob(t_confirmed_gain))
    )


print(t_confirmed_gain)

print(t_dates)


@tf.function(autograph=False)
def graph_sample_chain(*args, **kwargs):
    return tfp.mcmc.sample_chain(*args, **kwargs)


num_burnin_steps = 5000
num_results = 20000


initial_chain_state = [
    tf.cast(tf.reduce_mean(t_confirmed_gain), tf.float32) *
    tf.ones([], dtype=tf.float32, name="init_lambda1"),
    tf.cast(tf.reduce_mean(t_confirmed_gain), tf.float32) *
    tf.ones([], dtype=tf.float32, name="init_lambda2"),
    0.5 * tf.ones([], dtype=tf.float32, name="init_tau"),
]


unconstraining_bijectors = [
    tfp.bijectors.Exp(),
    tfp.bijectors.Exp(),
    tfp.bijectors.Sigmoid(),
]

step_size = 0.2

kernel = tfp.mcmc.TransformedTransitionKernel(
    inner_kernel=tfp.mcmc.HamiltonianMonteCarlo(
        target_log_prob_fn=joint_log_prob,
        num_leapfrog_steps=2,
        step_size=step_size,
        state_gradients_are_stopped=True),
    bijector=unconstraining_bijectors)

kernel = tfp.mcmc.SimpleStepSizeAdaptation(
    inner_kernel=kernel, num_adaptation_steps=int(num_burnin_steps * 0.8))


[
    lambda_1_samples,
    lambda_2_samples,
    posterior_tau,
], kernel_results = graph_sample_chain(
    num_results=num_results,
    num_burnin_steps=num_burnin_steps,
    current_state=initial_chain_state,
    kernel=kernel)

tau_samples = tf.floor(
    posterior_tau * tf.cast(len(dates), dtype=tf.float32))

print("tau_samples", tau_samples)

plt.subplot(311)
plt.bar(dates, confirmed_gain)
plt.title("Confirmed gain")
plt.xlabel("Date")
plt.ylabel("New cases")

plt.subplot(312)
plt.hist(confirmed_gain, bins=10)
plt.xlabel("New cases")
plt.ylabel("Number")

# FIXME: figure it out how to compute tau properly
plt.subplot(313)
# plt.bar(tau_samples, bins=20)
np_tau = tau_samples.numpy()
print("np_tau", np_tau)
plt.bar(np_tau - 1, confirmed_gain[np_tau - 1],
        color="r", label="Covid-19 confirmed gain changed")
plt.xlim(0, len(dates))

plt.show()
