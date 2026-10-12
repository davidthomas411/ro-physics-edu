"""Topic registry. Order inside a domain is the study order. Problems follow each topic's cards, so card ids stay stable."""
import waves_photons, particles_energy, charges_atom, nuclear_structure, decay_modes, decay_schemes, decay_law, specific_activity, equilibrium, xray_tube
import linac_components, photon_interactions, attenuation, neutron_interactions, charged_particles, kerma_dose, ion_chambers, tg51, dosimeters, pdd, tmr, scatter, mu_calc
import brachy_sources, brachy_exposure, tg43, brachy_qa, brachy_planning
import profiles, skin_bolus, dose_algorithms
import multifield, wedges, field_shaping
import electron_pdd, electron_fields, electron_mu
import icru_volumes, dvh_metrics, bed_tcp
import inverse_planning, imrt_delivery, mlc_imrt
import radiographic_quality, image_data, ct_reconstruction, ct_quality
import mri_physics, mri_sequences, mri_artifacts, spect, pet_imaging, ultrasound, simulation_motion, igrt
import qa_linac, dose_limits, shielding, risk_management, tbi_tset, rpt_iort, protons, srs_sbrt
import problems_decay
_ORDER = (waves_photons, particles_energy, charges_atom, nuclear_structure, decay_modes, decay_schemes, decay_law, specific_activity, equilibrium,
          xray_tube, linac_components, photon_interactions, attenuation, neutron_interactions, charged_particles, kerma_dose, ion_chambers, tg51, dosimeters, pdd, tmr, scatter, mu_calc, profiles, skin_bolus, dose_algorithms, multifield, wedges, field_shaping, electron_pdd, electron_fields, electron_mu, icru_volumes, dvh_metrics, bed_tcp, inverse_planning, imrt_delivery, mlc_imrt, radiographic_quality, image_data, ct_reconstruction, ct_quality, mri_physics, mri_sequences, mri_artifacts, spect, pet_imaging, ultrasound, simulation_motion, igrt, brachy_sources, brachy_exposure, tg43, brachy_qa, brachy_planning, qa_linac, dose_limits, shielding, risk_management, tbi_tset, rpt_iort, protons, srs_sbrt)
TOPICS = []
for _m in _ORDER:
    _t = dict(_m.TOPIC)
    _t["problems"] = list(getattr(_m, "PROBLEMS", [])) + list(problems_decay.EXTRA.get(_t["id"], []))
    _t["take"] = getattr(_m, "TAKE", None)
    _t["terms"] = getattr(_m, "TERMS", None)
    _t["inline"] = getattr(_m, "INLINE", None) or problems_decay.PLACE.get(_t["id"])
    TOPICS.append(_t)
import abr_style, more_content, more_xray_tube, more_linac_components, more_charged_particles, more_attenuation, more_neutron_interactions
abr_style.apply(TOPICS)
more_content.apply(TOPICS)
