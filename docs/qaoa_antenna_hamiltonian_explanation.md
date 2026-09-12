# QAOA Hamiltonian for the 5-Qubit Antenna-Tilt Encoding

For **our 5-qubit encoding**, the Hamiltonian is actually very clean conceptually.

I would slightly change notation so we don't confuse the physical tilts with the bitstring:

$$
\mathbf z=(z_1,\ldots,z_5)\in\{0,1\}^5
$$

is the **5-qubit computational state**, and it decodes to a physical three-sector configuration

$$
\mathbf t(\mathbf z)=(t_1,t_2,t_3).
$$

There are 32 possible bitstrings, of which 27 represent valid configurations.

## 1. First turn utility into cost

We have

$$
U(\mathbf t)
=
\alpha Q(\mathbf t)
-\beta I(\mathbf t)
-\gamma D(\mathbf t).
$$

QAOA should favor the **lowest-energy state**, so define

$$
\boxed{
C(\mathbf t)
=
-U(\mathbf t)
=
-\alpha Q(\mathbf t)
+\beta I(\mathbf t)
+\gamma D(\mathbf t)
}
$$

Therefore, for every valid bitstring $\mathbf z$,

$$
\boxed{
E(\mathbf z)
=
-\alpha Q(\mathbf t(\mathbf z))
+\beta I(\mathbf t(\mathbf z))
+\gamma D(\mathbf t(\mathbf z)).
}
$$

This number becomes the energy of that state.

## 2. Cost Hamiltonian

The exact Hamiltonian is

$$
\boxed{
H_C
=
\sum_{\mathbf z\in\mathcal V}
E(\mathbf z)
|\mathbf z\rangle\langle\mathbf z|
+
E_{\rm invalid}
\sum_{\mathbf z\notin\mathcal V}
|\mathbf z\rangle\langle\mathbf z|
}
$$

where

$$
\mathcal V
$$

is the set of the 27 valid bitstrings.

So literally:

> take every possible antenna configuration, calculate its utility, negate it, and assign that value as the energy of its corresponding quantum basis state.

The 5 unused states get a deliberately high energy

$$
E_{\rm invalid}
$$

so QAOA avoids them.

For example, if one configuration has

$$
U=2.7,
$$

then

$$
C=-2.7
$$

and its basis state gets energy $-2.7$.

If another has

$$
U=0.8,
$$

its energy is

$$
-0.8.
$$

Thus the better configuration has lower energy:

$$
-2.7<-0.8.
$$

Exactly what we want.

## 3. How does this become gates?

Every projector can be written using $Z$ operators.

For one qubit,

$$
|0\rangle\langle0|=\frac{I+Z}{2},
\qquad
|1\rangle\langle1|=\frac{I-Z}{2}.
$$

So for a 5-bit state

$$
\mathbf z=z_1z_2z_3z_4z_5,
$$

$$
\boxed{
|\mathbf z\rangle\langle\mathbf z|
=
\prod_{j=1}^{5}
\frac{I+(-1)^{z_j}Z_j}{2}.
}
$$

Therefore our Hamiltonian can be expanded into

$$
\boxed{
H_C
=
c_0I
+\sum_i c_iZ_i
+\sum_{i<j}c_{ij}Z_iZ_j
+\sum_{i<j<k}c_{ijk}Z_iZ_jZ_k
+\cdots
+c_{12345}Z_1Z_2Z_3Z_4Z_5.
}
$$

That is the actual Pauli-$Z$ Hamiltonian the quantum circuit implements.

## 4. Then QAOA uses it

The cost layer is

$$
\boxed{
U_C(\gamma)=e^{-i\gamma H_C}.
}
$$

So each basis state acquires a phase according to its antenna cost:

$$
|\mathbf z\rangle
\rightarrow
e^{-i\gamma E(\mathbf z)}
|\mathbf z\rangle.
$$

Then the standard mixer Hamiltonian is

$$
\boxed{
H_M=\sum_{j=1}^{5}X_j
}
$$

and

$$
U_M(\beta)=e^{-i\beta H_M}.
$$

One QAOA layer is therefore

$$
\boxed{
e^{-i\beta H_M}
e^{-i\gamma H_C}.
}
$$

After several layers, a classical optimizer finds the $\gamma$'s and $\beta$'s that lower the measured average cost.

This is exactly the pattern used in the Qubit IL/Classiq workshop: **define the classical objective, apply it through the phase/cost layer, apply the $X$-mixer, and classically optimize the QAOA parameters.**

## The important consequence of our 5-qubit choice

Because we've chosen **minimum qubits**, $H_C$ will generally not be only

$$
Z_i,\quad Z_iZ_j.
$$

It can contain terms up to

$$
Z_1Z_2Z_3Z_4Z_5.
$$

That's the trade:

$$
\boxed{\text{fewer qubits} \Longleftrightarrow \text{potentially more complicated Hamiltonian}.}
$$

For our **5-qubit toy problem**, that's quite reasonable. For scaling to many interaction regions, this is exactly the issue we'll eventually need the classical decomposition strategy to manage.
