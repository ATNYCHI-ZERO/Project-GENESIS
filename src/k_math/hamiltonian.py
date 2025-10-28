import pennylane as qml
from pennylane import numpy as np

print("K-MATH: Loading KHamiltonian Evolution Module...")

# Define a default quantum device
dev_hamiltonian = qml.device("default.qubit", wires=2)

def KHamiltonianStep(params, time_t=0.1):
    """
    This is the core KHamiltonian operator.
    
    As discussed, this is the SYMPLECTIC STEP that drives
    the evolution of the system. We model this as a Hamiltonian
    that evolves for a short time 't'.
    """
    
    # 1. Define the Hamiltonian (the 'K' operator)
    # This is a placeholder. You would define your actual
    # K-Math Hamiltonian here.
    coeffs = [params[0], params[1]]
    obs = [qml.PauliX(0) @ qml.PauliX(1), qml.PauliZ(0) @ qml.PauliZ(1)]
    
    H = qml.Hamiltonian(coeffs, obs)
    
    # 2. Apply the time evolution (the symplectic step)
    # This is the command that simulates the Hamiltonian
    qml.ApproxTimeEvolution(H, time_t, 1)


@qml.qnode(dev_hamiltonian)
def full_k_math_circuit(params, resonance_params):
    """
    This circuit combines BOTH operators, as planned.
    1. KResonance (Phase Operator)
    2. KHamiltonian (Symplectic Step)
    """
    
    # --- PHASE 1: KResonance (from resonance.py) ---
    # We can't import directly in this example, so we'll 
    # re-define a simple version.
    qml.PhaseShift(resonance_params[0], wires=0)
    qml.CZ(wires=[0, 1])
    
    # --- PHASE 2: KHamiltonian (from this file) ---
    KHamiltonianStep(params, time_t=0.5)
    
    # Measure the result
    return qml.expval(qml.PauliZ(0))


if __name__ == "__main__":
    # This part runs if you execute the file directly
    print("Testing full K-Math (Resonance + Hamiltonian) circuit...")
    
    # Initialize parameters
    h_params = np.array([0.4, 0.5], requires_grad=True)
    r_params = np.array([0.1], requires_grad=True)
    
    result = full_k_math_circuit(h_params, r_params)
    
    print(f"Full K-Math circuit test complete.")
    print(f"Result (expval): {result}")

