from blocks import *
import math, calc

cost = lambda doses, d0, w: w * sum((d - d0) ** 2 for d in doses)                  # f = w * sum of (d_i - d_Rx)^2 over the voxels
over = lambda doses, d0, w: w * sum((d - d0) ** 2 for d in doses if d > d0)        # an upper objective penalizes only the voxels above the limit
f_t = cost([76, 78, 80], 78, 1.0)
f_o1, f_o3 = over([35, 45], 30, 0.1), over([35, 45], 30, 0.3)
f_tot1, f_tot3 = f_t + f_o1, f_t + f_o3
trade = lambda r: (20 + 12 / (1 + r), 78 - 8 * r / (1 + r))                          # schematic: OAR mean dose and target D95 as the OAR weight ratio r grows

TOPIC = dict(
    id="inverse-planning", domain=3, sub="III.D", title="Inverse planning and optimization",
    ref=dict(aapm="TG-119, TG-218", khan="20", ford="14"),
    guide=[
        H("Forward and inverse planning"),
        P("[[1|In forward planning the planner chooses the beam angles and the MLC shape for each beam, and the computer calculates the dose distribution.]] The planner looks at the result and adjusts the beams, so it is a manual and iterative process. It is the usual way to plan a three-dimensional conformal treatment, for example six fields shaped to the target and angled to avoid the femoral heads in a prostate plan."),
        P("Inverse planning inverts this. [[1|The planner specifies the dose distribution that is wanted, and the computer works out the fluence of the beams, and from it the MLC leaf sequence, that comes closest to it.]] The planner still chooses the beam arrangement, for example five to nine fixed gantry angles for IMRT or one or two arcs for VMAT. Inverse planning is how IMRT and VMAT plans are made."),
        H("Cost functions and optimization"),
        P("Inverse planning is an optimization problem. A measure of how far a plan is from the wanted dose, called the cost function, is minimized, and the dose-volume histogram is the usual way to state what is wanted. For a target treated uniformly, the ideal DVH holds 100% of the volume at the prescription dose and then falls abruptly to zero."),
        EQ("[[1|f = w Σ<sub>i</sub> (d<sub>i</sub> − d<sub>Rx</sub>)²]]", "d<sub>i</sub> = dose in voxel i,   d<sub>Rx</sub> = the intended dose,   w = weight of the objective"),
        P("The sum runs over all voxels of the structure. [[1|The difference between the dose in a voxel and the intended dose is squared so that it cannot be negative, so large deviations are penalized heavily.]] If every voxel received the intended dose, the cost would be zero. An objective on a normal tissue is a limit on its DVH, for example that no more than 30% of the rectum receives a given dose, and it penalizes only the voxels above the limit."),
        EX("A cost function for a target", STEM("Three voxels of a target with an intended dose of 78 Gy, a weight w = 1.", ["voxel doses 76, 78, and 80 Gy"], "Find the [[cost]]."), ["f = 1 × [ (76 − 78)² + (78 − 78)² + (80 − 78)² ]"], f"f = 4 + 0 + 4 = {f_t:.0f}. A voxel at 70 Gy alone would cost {cost([70], 78, 1):.0f}, so a large shortfall is penalized much more than a small one."),
        P("The target and the organs at risk compete. Sparing an organ lowers the dose in the part of the target nearest to it, so the target DVH develops a shoulder below the prescription dose. [[1|Each objective carries a weight.]] Raising the weight of the organ-at-risk term relative to the target term gives priority to sparing, and lowering it gives priority to coverage. Several organs, and other measures such as how tightly the dose conforms to the target or how the low doses spill into normal tissue, can be added as further terms. The optimization changes the fluence until the total cost is as small as possible. The result is the best compromise for the weights that were chosen, and a different set of weights gives a different plan."),
        EX("Weights", STEM("A total cost has a target term and an organ term.", ["target voxels 76, 78, 80 Gy against 78 Gy, weight 1", "organ voxels 35 and 45 Gy against an upper limit of 30 Gy", "organ weight 0.1, then 0.3"], "Find the [[total cost]] for each organ weight."), ["Target: 4 + 0 + 4 = 8", "Organ term = w × [ (35 − 30)² + (45 − 30)² ] = w × 250"], f"With w = 0.1: {f_t:.0f} + {f_o1:.0f} = {f_tot1:.0f}. With w = 0.3: {f_t:.0f} + {f_o3:.0f} = {f_tot3:.0f}. The larger weight makes the organ dose count three times as much, so the optimizer will lower the organ dose even if the target coverage suffers."),
        H("Settings chosen by the planner"),
        P("The planner sets the objectives, which are dose and volume limits on each structure, and their weights or priorities. The quantity that the optimizer changes is the fluence of the beams across each field, and a leaf sequence that delivers it is calculated afterwards. The dose is then recalculated with the full algorithm, because the optimization uses a simplified model. [[1|A plan with a lower cost is better only for the objectives and weights that were given,]] so the planner judges the plan on the DVH and the dose distribution as well. [[1|Raising the weight of an organ term lowers the organ dose and lowers the target coverage.]]"),
    ],
    cards=[
        F("Forward planning", "The planner chooses the beam angles and MLC shapes and the computer calculates the dose. A manual, iterative process, usual for 3D conformal plans."),
        F("Inverse planning", "The planner specifies the wanted dose distribution, and the computer calculates the fluence and the MLC leaf sequence that come closest to it."),
        F("Planner choices in inverse planning", "The beam arrangement, such as five to nine fixed gantry angles for IMRT or one or two arcs for VMAT."),
        F("Inverse planning as optimization", "A cost function measures how far a plan is from the wanted dose, and the optimizer changes the fluence until the cost is as small as possible."),
        F("Quadratic cost function", "f = w Σ (d<sub>i</sub> − d<sub>Rx</sub>)² over the voxels. Squaring keeps it positive and penalizes large deviations heavily."),
        F("Objectives for organs at risk", "Limits on the DVH, for example that no more than 30% of the rectum receives a stated dose. They penalize only the voxels above the limit."),
        F("Weights", "Raising the weight of the organ term relative to the target term prioritizes sparing over coverage, and lowering it prioritizes coverage."),
        F("Quantity the optimizer changes", "The fluence of the beams across each field. The leaf sequence that delivers it is calculated afterwards."),
        F("Meaning of a low cost", "A plan with a lower cost is better only for the objectives and weights that were given. The DVH and the dose distribution are still reviewed."),
    ],
)

PROBLEMS = [
    PR("In forward planning, the planner specifies:", "the beam angles and MLC shapes, and the computer calculates the dose", ["the wanted dose distribution, and the computer calculates the MLC shapes", "only the prescription dose", "nothing, because the computer chooses everything"],
       "Inverse planning reverses this: the dose is specified and the fluence is calculated.", lvl="Easy"),
    PR("Inverse planning is described as an optimization problem because it:", "minimizes a cost function that measures how far the plan is from the wanted dose", ["maximizes the number of monitor units", "searches for the beam energy with the lowest cost", "calculates the dose with a Monte Carlo method"],
       "The optimizer changes the fluence until the cost function is as small as possible.", lvl="Easy"),
    PR("The quantity that the optimizer changes in IMRT inverse planning is:", "the fluence across each beam", ["the beam energy", "the patient contour", "the prescription dose"],
       "A leaf sequence that delivers the optimized fluence is calculated afterwards.", lvl="Easy"),
    PRN(STEM("A target has an intended dose of 78 Gy. Three voxels receive 76, 78, and 80 Gy.", ["cost function f = w Σ (d<sub>i</sub> − d<sub>Rx</sub>)², with w = 1"], "What is [[f]]?"), f_t, [0.0, 4.0, 16.0], "{:.0f}",
        f"f = (−2)² + 0² + 2² = {f_t:.0f}. Adding the deviations before squaring gives 0, adding their absolute values gives 4, and squaring that sum gives 16.", lvl="Moderate"),
    PR("Why is the difference between the dose and the intended dose squared in the cost function?", "So that it cannot be negative, and so that large deviations are penalized heavily", ["So that the dose is always above the prescription", "So that the optimization finishes faster", "So that the organs at risk are ignored"],
       "Without the square, an overdose and an underdose would cancel, and the sum could be zero for a poor plan.", lvl="Moderate"),
    PR("The weight of the rectum objective is increased relative to the target objective. The optimized plan will tend to:", "spare the rectum more, at some cost to target coverage", ["cover the target more uniformly", "increase the dose to the rectum", "leave the plan unchanged"],
       "A larger weight makes the organ dose count more in the total cost, so the optimizer will lower it.", lvl="Moderate"),
    PR("A plan with a lower value of the cost function than another plan is:", "better only for the objectives and weights that were used", ["always the better plan clinically", "always the more deliverable plan", "always the plan with the lower organ dose"],
       "The cost function encodes the planner's choices. Different weights can reverse the ranking, so plans are also judged on the DVH and the dose distribution.", lvl="Challenging"),
    PR("An IMRT optimization uses a simplified dose model, and the final dose is recalculated with the full algorithm. The reason is that:", "the optimization needs many fast calculations, and the final dose must be accurate", ["the full algorithm cannot be used for optimization in principle", "the simplified model is always more accurate", "recalculation changes the beam energy"],
       "Optimization evaluates the dose many times, so a fast model is used, and the accurate calculation is made once at the end.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4, 5, 6], 2: [7]}

TERMS = ['forward planning', 'inverse planning', 'cost function', 'fluence']

TAKE = [
    [('In forward planning the planner chooses the beams and the computer calculates the dose. In inverse planning the planner specifies the dose and the computer calculates the fluence.', 'forward-inverse')],
    [('The cost function f = w Σ (d<sub>i</sub> − d<sub>Rx</sub>)² grows with the square of each deviation. Weights set how much each structure counts.', 'cost-function')],
    [('Raising the weight of an organ lowers its dose and lowers target coverage. The optimized plan is a compromise for the weights chosen.', 'plan-tradeoff')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
PROBLEMS += [
]
