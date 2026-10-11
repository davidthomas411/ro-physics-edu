"""ABR Medical Physics for Radiation Oncology: seven domains and their subsections (ABR study guide, 2023 edition).
Weights are the ranges the ABR gives for guidance."""
DOMAINS = [
    dict(n=1, roman="I", name="Basic physics", short="Basic physics", lines=["Basic physics"], linesM=["Basic physics"], weight="11% to 13%", subs=[
        ("I.A", "Fundamental physics"), ("I.B", "Atomic and nuclear structure"),
        ("I.C", "Production of kilovoltage x-ray beams"), ("I.D", "Production of megavoltage x-ray beams"),
        ("I.E", "Radiation interactions")]),
    dict(n=2, roman="II", name="Radiation measurements", short="Measurements", lines=["Radiation", "measurements"], linesM=["Radiation", "measurements"], weight="9% to 11%", subs=[
        ("II.A", "Radiation quantities and units"), ("II.B", "Radiation measurement and calibration")]),
    dict(n=3, roman="III", name="Treatment planning", short="Treatment planning", lines=["Treatment planning"], linesM=["Treatment", "planning"], weight="19% to 21%", subs=[
        ("III.A", "Photon beam characteristics and dosimetry"), ("III.B", "Electron beam characteristics and dosimetry"),
        ("III.C", "Prescribing, reporting, and evaluating radiotherapy treatment plans"), ("III.D", "Intensity modulated radiation therapy (IMRT)")]),
    dict(n=4, roman="IV", name="Imaging modalities and applications in radiotherapy", short="Imaging", lines=["Imaging modalities and", "applications in", "radiotherapy"], linesM=["Imaging modalities", "and applications", "in radiotherapy"], weight="16% to 18%", subs=[
        ("IV.A", "Imaging fundamentals"), ("IV.B", "Simulation, motion management, image guidance, and treatment verification")]),
    dict(n=5, roman="V", name="Brachytherapy", short="Brachytherapy", lines=["Brachytherapy"], linesM=["Brachytherapy"], weight="12% to 14%", subs=[("V", "Brachytherapy")]),
    dict(n=6, roman="VI", name="Advanced treatment planning and special procedures", short="Special procedures", lines=["Advanced treatment", "planning and special", "procedures"], linesM=["Advanced", "treatment", "planning and", "special", "procedures"], weight="15% to 17%", subs=[
        ("VI.A", "Special procedures (TBI, TSET, IORT, radiopharmaceutical treatment)"), ("VI.B", "Particle therapy"),
        ("VI.C", "Stereotactic radiosurgery and stereotactic body radiation therapy")]),
    dict(n=7, roman="VII", name="Safety, QA, and radiation protection", short="Safety and QA", lines=["Safety, QA, and", "radiation protection"], linesM=["Safety, QA, and", "radiation", "protection"], weight="11% to 13%", subs=[
        ("VII.A", "Quality assurance"), ("VII.B", "Radiation protection and shielding"), ("VII.C", "Safety and incidents")]),
]
