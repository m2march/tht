'''Default configuration for THT'''

from . import confidence
from . import correction
from . import similarity

eval_f = confidence.all_history_eval
corr_f = correction.lin_r_corr_opt
sim_f = similarity.min_dist_sim
similarity_epsilon = 0.005
max_delta = (60000.0 / 40),  # 40 bpm
min_delta = (60000.0 / 320)  # 320 bpm
max_hypotheses = 30

config = {
    'eval_f': eval_f,
    'corr_f': corr_f,
    'sim_f': sim_f,
    'similarity_epsilon': similarity_epsilon,
    'max_delta': max_delta,
    'min_delta': min_delta,
    'max_hypotheses': max_hypotheses
}
