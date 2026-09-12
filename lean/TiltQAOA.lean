/-
# Tilt-QAOA certificates

This module formalizes the binary antenna-tilt encoding, the scaled integer
cost function and its exhaustive optimum certificate, and elementary facts
used by the QAOA cost Hamiltonian.
-/

import Mathlib.Tactic

/-- Decode the low and high qubits as the two-bit tilt `q0 + 2*q1`. -/
def decodeTilt (q0 q1 : Fin 2) : Fin 4 :=
  ⟨q0.val + 2 * q1.val, by omega⟩

/-- Encode a tilt as its low and high bits. -/
def encodeTilt (t : Fin 4) : Fin 2 × Fin 2 :=
  (⟨t.val % 2, Nat.mod_lt _ (by omega)⟩, ⟨t.val / 2, by omega⟩)

/-- Decoding the encoding of a tilt returns that tilt. -/
theorem decode_encode_tilt : ∀ t, decodeTilt (encodeTilt t).1 (encodeTilt t).2 = t := by
  decide

/-- Encoding decoded qubits returns the original pair of bits. -/
theorem encode_decode_tilt : ∀ q0 q1, encodeTilt (decodeTilt q0 q1) = (q0, q1) := by
  decide

/-- Corollary: every two-qubit bit string is valid, and every tilt has exactly one encoding. -/
theorem decodeTilt_bijective : Function.Bijective (fun q : Fin 2 × Fin 2 => decodeTilt q.1 q.2) := by
  constructor
  · intro a b h
    have := congrArg encodeTilt h
    simpa [encode_decode_tilt] using this
  · intro t
    exact ⟨encodeTilt t, decode_encode_tilt t⟩

/-- Maximizing utility is equivalent to minimizing its negative. -/
theorem maximize_utility_iff_minimize_negative {α : Type*} (U : α → ℤ) (x : α) :
    (∀ y, U y ≤ U x) ↔ (∀ y, -U x ≤ -U y) := by
  constructor <;> intro h y <;> linarith [h y]

/-- The interference matrix, scaled by 10000. -/
def imatS : Fin 6 → Fin 6 → ℤ := ![
  ![0, 13500, 13500, 1807, 1807, 1807],
  ![13500, 0, 13500, 1851, 1851, 1851],
  ![13500, 13500, 0, 1741, 1741, 1741],
  ![1807, 1851, 1741, 0, 13500, 13500],
  ![1807, 1851, 1741, 13500, 0, 13500],
  ![1807, 1851, 1741, 13500, 13500, 0]
]

/-- The linear coverage coefficients, scaled by 15000. -/
def cvecS : Fin 6 → ℤ := ![12225, 12480, 12225, 12000, 12000, 12000]

/-- The antenna cost, scaled by 10000 so that every coefficient is integral. -/
def costS (t : Fin 6 → Fin 4) : ℤ :=
  ∑ i, ∑ j, imatS i j * (t i).val * (t j).val
    - ∑ i, cvecS i * (t i).val
    + 3000 * ∑ i, (t i).val

/-- The unique optimal antenna tilt assignment. -/
def optTilt : Fin 6 → Fin 4 := ![0, 3, 0, 0, 0, 0]

/-- The claimed assignment has scaled cost `-28440`. -/
theorem costS_optTilt : costS optTilt = -28440 := by
  decide

/-- Exhaustive compiled certificate: no assignment has cost below `-28440`. -/
theorem costS_lower_bound : ∀ t : Fin 6 → Fin 4, -28440 ≤ costS t := by
  native_decide

/-- Exhaustive compiled certificate: the optimum assignment is unique. -/
theorem costS_unique : ∀ t : Fin 6 → Fin 4, costS t = -28440 → t = optTilt := by
  native_decide

/-- Every QAOA cost phase has unit norm. -/
theorem cost_phase_norm : ∀ γ c : ℝ, ‖Complex.exp ((γ * c : ℝ) * Complex.I)‖ = 1 := by
  intro γ c
  exact Complex.norm_exp_ofReal_mul_I (γ * c)

/-- Multiplication by a cost phase preserves each amplitude's norm. -/
theorem cost_phase_preserves_amplitude :
    ∀ (γ c : ℝ) (a : ℂ), ‖Complex.exp ((γ * c : ℝ) * Complex.I) * a‖ = ‖a‖ := by
  intro γ c a
  rw [Complex.norm_mul, cost_phase_norm, one_mul]

/-- Consequently, a cost phase preserves the basis-state measurement probability. -/
theorem cost_phase_preserves_probability :
    ∀ (γ c : ℝ) (a : ℂ), ‖Complex.exp ((γ * c : ℝ) * Complex.I) * a‖ ^ 2 = ‖a‖ ^ 2 := by
  intro γ c a
  rw [cost_phase_preserves_amplitude]

/-- The Pauli-Z matrix over the rationals. -/
def Z : Matrix (Fin 2) (Fin 2) ℚ := !![1, 0; 0, -1]

/-- Projector onto the zero computational basis state. -/
def P0 : Matrix (Fin 2) (Fin 2) ℚ := !![1, 0; 0, 0]

/-- Projector onto the one computational basis state. -/
def P1 : Matrix (Fin 2) (Fin 2) ℚ := !![0, 0; 0, 1]

/-- The zero-state projector satisfies `2 P0 = I + Z`. -/
theorem two_smul_P0 : (2 : ℚ) • P0 = 1 + Z := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [Z, P0, Matrix.one_apply]

/-- The one-state projector satisfies `2 P1 = I - Z`. -/
theorem two_smul_P1 : (2 : ℚ) • P1 = 1 - Z := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [Z, P1, Matrix.one_apply]
