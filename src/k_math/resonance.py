import pennylane as qml
from pennylane import numpy as np

print("K-MATH: Loading KResonance Operator Module...")

# Define a default quantum device (simulator)
# 'wires=2' means we are using 2 qubits.
dev_resonance = qml.device("default.qubit", wires=2)

def KResonanceOperator(params):
    """
    This is the core KResonance operator.
    
    As discussed, this is a PHASE OPERATOR. It encodes the
    harmonic "breathing" loop. We model this using phase-shift
    and controlled-phase gates.
    """
    # Example: A simple, parameterized phase-encoding circuit
    qml.PhaseShift(params[0], wires=0)
    qml.PhaseShift(params[1], wires=1)
    qml.CZ(wires=[0, 1]) # Controlled-Phase operation
    qml.RY(params[2], wires=0) # Resonance 'pulse'

@qml.qnode(dev_resonance)
def resonance_circuit(params):
    """
    This is the full quantum circuit (QNode) that runs
    the KResonanceOperator and measures the result.
    """
    # Apply the KResonance operator
    KResonanceOperator(params)
    
    # Measure the expectation value of the first qubit
    return qml.expval(qml.PauliZ(0))

if __name__ == "__main__":
    # This part runs if you execute the file directly
    print("Testing KResonance circuit...")
    
    # Initialize random parameters for the operator
    test_params = np.array([0.1, 0.2, 0.3], requires_grad=True)
    
    result = resonance_circuit(test_params)
    
    print(f"KResonance circuit test complete.")
    print(f"Parameters: {test_params}")
    print(f"Result (expval): {result}")
