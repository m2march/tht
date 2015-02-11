

import confidence
import correction
import similarity

similarity_epsilon = 0.005

config = {
    'eval_f': confidence.eval,
    'corr_f': correction.lin_r_corr_opt,
    'sim_f': similarity.min_dist_sim,
    'similarity_epsilon': similarity_epsilon,
    'max_delta': (60000.0 / 40),  # 40 bpm
    'min_delta': (60000.0 / 320)  # 320 bpm
}
