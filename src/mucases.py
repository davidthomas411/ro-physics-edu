"""The curated MU calculation cases. Each case is one field of a treatment: the module works out the MU for it.

Fields of a case
  level    Easy, Moderate, or Challenging
  E        photon energy in MV (6, 10, 15, 18)
  tech     SSD or SAD
  f        SSD in cm, for the SSD technique (the SAD technique is 100 cm)
  cal      calibration convention: SSD (1 cGy/MU at d_max, surface at 100 cm) or SAD (1 cGy/MU at d_max, point at 100 cm)
  field    side lengths a, b in cm, at the surface for SSD and at the isocenter for SAD
  d        depth of the point in cm
  dose     dose to the point from all fields, in cGy
  w        the share of that dose delivered by this field
  wedge    wedge angle in degrees, or 0
  tray     True if a blocking tray is in the beam
  ctx      one line of setting
  note     one line of teaching point, shown with the solution
"""

def C(level, E, tech, field, d, dose, f=100, cal="SSD", w=1.0, wedge=0, tray=False, ctx="", note=""):
    return dict(level=level, E=E, tech=tech, f=f if tech == "SSD" else 100, cal=cal, field=list(field), d=d, dose=dose, w=w, wedge=wedge, tray=tray, ctx=ctx, note=note)

CASES = [
    # ------------------------------------------------------------ Easy: open fields, tabulated values
    C("Easy", 6, "SSD", (10, 10), 5, 200, ctx="Open field, SSD technique.", note="At SSD 100 cm with an SSD calibration, the inverse-square term is 1."),
    C("Easy", 6, "SSD", (15, 15), 10, 180, ctx="Larger field at mid-depth.", note="Sc and Sp both rise with field size, and the PDD does too."),
    C("Easy", 6, "SSD", (20, 20), 8, 250, ctx="Large field, shallow target.", note="Read all three factors from the 20 × 20 cm column."),
    C("Easy", 6, "SSD", (10, 10), 15, 200, ctx="Deeper target.", note="A lower PDD at depth means more MU for the same dose."),
    C("Easy", 6, "SAD", (10, 10), 5, 200, ctx="The setup of case 1, treated isocentrically.", note="With an SSD calibration, the SAD technique has an inverse-square term of (100 + d_max)²/100², which is 1.030 for 6 MV."),
    C("Easy", 6, "SAD", (15, 15), 10, 180, ctx="Isocentric field, mid-depth.", note="The TMR replaces the PDD, and the inverse-square term is the same as in every SAD case with this calibration."),
    C("Easy", 6, "SAD", (20, 20), 12, 300, ctx="Large isocentric field.", note="TMR is read for the field size at the point, here the isocenter."),
    C("Easy", 6, "SAD", (10, 10), 15, 200, ctx="Deeper isocenter.", note="The TMR falls with depth more slowly than the PDD does, because it has no inverse-square fall-off."),
    C("Easy", 10, "SSD", (10, 10), 10, 200, ctx="A 10 MV beam: use the 10 MV tables.", note="Each energy has its own tables. At SSD 100 cm the inverse-square term is still 1."),
    C("Easy", 15, "SAD", (10, 10), 10, 200, ctx="A 15 MV isocentric field.", note="The inverse-square term depends on d_max: (100 + 3.0)²/100² = 1.061 for 15 MV."),
    C("Easy", 18, "SSD", (15, 15), 12, 180, ctx="An 18 MV field, SSD technique.", note="The 18 MV PDD falls off more slowly than the 6 MV PDD, so fewer MU are needed at depth."),
    C("Easy", 18, "SAD", (10, 10), 15, 200, ctx="An 18 MV isocentric field.", note="The inverse-square term is (100 + 3.5)²/100² = 1.071."),
    # ------------------------------------------------------------ Moderate: interpolation, rectangles, modifiers, opposed fields, calibration, extended SSD
    C("Moderate", 6, "SSD", (7, 7), 10, 200, ctx="A 7 × 7 cm field is not in the tables.", note="Interpolate Sc, Sp, and the PDD between the 6 × 6 and 8 × 8 cm columns."),
    C("Moderate", 6, "SAD", (10, 10), 7.5, 200, ctx="A depth between two rows of the table.", note="7.5 cm lies halfway between the 7 and 8 cm rows of the TMR table."),
    C("Moderate", 6, "SSD", (8, 12), 10, 200, ctx="A rectangular field at the surface.", note="Use the equivalent square, 2ab/(a + b), for Sc, Sp, and the PDD."),
    C("Moderate", 6, "SAD", (8, 12), 10, 180, ctx="A rectangular field at the isocenter.", note="The equivalent square of 8 × 12 cm is 9.6 cm, between the 8 and 10 cm columns."),
    C("Moderate", 6, "SSD", (10, 10), 8, 200, wedge=45, ctx="A 45° wedge.", note="The wedge factor divides the dose per MU, so it raises the MU."),
    C("Moderate", 15, "SAD", (10, 10), 10, 150, wedge=30, tray=True, ctx="A 30° wedge in a blocking tray.", note="Both the wedge factor and the tray factor lower the dose per MU."),
    C("Moderate", 6, "SSD", (15, 15), 10, 200, w=0.5, ctx="An AP/PA pair, equally weighted. The patient is 20 cm thick and 200 cGy is prescribed to the midplane.", note="Each field gives half of the dose to the midplane, which is 10 cm deep for each of them."),
    C("Moderate", 10, "SAD", (12, 12), 13, 180, w=0.5, ctx="An AP/PA pair, equally weighted. The patient is 26 cm thick and 180 cGy is prescribed to the isocenter at the midplane.", note="The isocenter is at 13 cm depth for each field, so each field delivers 90 cGy."),
    C("Moderate", 10, "SAD", (10, 10), 10, 200, cal="SAD", ctx="This machine is calibrated with the SAD convention.", note="With a SAD calibration, the inverse-square term of the SAD technique is 1."),
    C("Moderate", 6, "SSD", (10, 10), 8, 200, f=110, ctx="Extended SSD, 110 cm.", note="The PDD table is for SSD 100 cm. Correct it with the Mayneord F factor, and include the inverse-square term for the longer SSD."),
    C("Moderate", 6, "SSD", (12, 12), 10, 200, f=120, ctx="Extended SSD, 120 cm, with a 12 × 12 cm field at the surface.", note="The collimator opening is 12 × 100/120 = 10 cm, so Sc is read for 10 × 10 cm and Sp for 12 × 12 cm."),
    C("Moderate", 18, "SSD", (10, 10), 10, 200, tray=True, ctx="A blocking tray in the beam.", note="The tray factor lowers the dose per MU and raises the MU."),
    # ------------------------------------------------------------ Challenging: several effects together
    C("Challenging", 6, "SSD", (10, 16), 6.5, 200, f=130, wedge=30, tray=True, ctx="A rectangular field at an extended SSD of 130 cm, with a 30° wedge and a blocking tray.", note="Work through the field sizes first. Sc uses the collimator opening and Sp uses the field at the surface."),
    C("Challenging", 10, "SAD", (10, 10), 9, 200, w=0.5, wedge=45, ctx="A wedge pair with a 90° hinge angle, equally weighted, 200 cGy to the isocenter.", note="Each field gives 100 cGy to the isocenter. The 45° wedge factor applies to each."),
    C("Challenging", 6, "SAD", (12, 14), 16, 200, w=0.4, ctx="The PA field of a 3:2 AP:PA pair, 200 cGy to a point 16 cm from the posterior surface.", note="The PA field gives 40% of the dose, and its depth is the distance from the posterior surface."),
    C("Challenging", 15, "SSD", (25, 25), 20, 200, tray=True, ctx="A large, deep field with a blocking tray.", note="At 25 × 25 cm the PDD and the scatter factors are all well above their 10 × 10 cm values."),
    C("Challenging", 18, "SAD", (30, 30), 20, 180, ctx="A large isocentric field at depth.", note="Check which column and row of each table to use before reading."),
    C("Challenging", 6, "SSD", (10, 10), 10, 200, cal="SAD", ctx="An SSD treatment on a machine calibrated with the SAD convention.", note="With a SAD calibration, the SSD technique at 100 cm has an inverse-square term of (100/(100 + d_max))², which is below 1."),
    C("Challenging", 6, "SSD", (10, 10), 10, 200, f=90, ctx="A short SSD of 90 cm.", note="The Mayneord F factor is below 1 at a shorter SSD, and the inverse-square term is above 1."),
    C("Challenging", 10, "SSD", (12, 15), 12.5, 220, f=115, wedge=45, ctx="A rectangular field at SSD 115 cm with a 45° wedge, at a depth between two rows.", note="Combine the equivalent square, the collimator projection, interpolation in depth, the Mayneord F factor, and the wedge factor."),
]
for _i, _c in enumerate(CASES, 1): _c["id"] = _i
