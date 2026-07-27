# Observable commercial information exposure metric

## Definition

The observable exposure score $E$ is a weighted sum of five component scores:

$$E = w_1 \cdot E_\text{direct} + w_2 \cdot E_\text{corridor} + w_3 \cdot E_\text{temporal} + w_4 \cdot E_\text{bottleneck} + w_5 \cdot E_\text{side}$$

Default weights (main scheme): $w = [0.25, 0.20, 0.20, 0.20, 0.15]$.

## Components

### $E_\text{direct}$ — Direct value exposure
Fraction of streams for which exact flow values are revealed in ADMM messages,
averaged across iterations.

$$E_\text{direct} = \frac{1}{T} \sum_{t=1}^{T} \frac{|\{s : s \in \text{exact\_keys}(m_t)\}|}{|S|}$$

### $E_\text{corridor}$ — Corridor (interval) exposure
Measures how narrow the revealed intervals are relative to each stream's capacity.
A narrow interval ($\text{width}/\text{cap} \approx 0$) leaks almost as much information as an exact value.

$$E_\text{corridor} = \frac{1}{T} \sum_{t=1}^{T} \frac{1}{|S|} \sum_{s \in \text{interval\_keys}(m_t)} \max\!\left(0,\; 1 - \frac{\text{width}_s(t)}{\text{cap}_s}\right)$$

### $E_\text{temporal}$ — Temporal trajectory exposure
Fraction of streams whose value trajectories across iterations can be reconstructed
by an observer.  A stream contributes if it appears as an exact value in any iteration,
or if its interval narrowness falls below 10% of capacity across iterations.

### $E_\text{bottleneck}$ — Bottleneck stream exposure
Fraction of streams that are observed to be at or near their capacity bound,
revealing binding production constraints.

$$E_\text{bottleneck} = \frac{1}{T} \sum_{t=1}^{T} \frac{|\{s : f_s(t) \geq 0.95 \cdot \text{cap}_s,\; s \notin \text{masked}\}|}{|S|}$$

### $E_\text{side}$ — Side-channel (active-set) exposure
The number of visible streams in each message reveals the size and composition of
the active production set, which is itself commercially sensitive.

$$E_\text{side} = \frac{1}{T} \sum_{t=1}^{T} \frac{|\text{visible\_streams}(m_t)|}{|S|}$$

## Scope

The exposure score measures **observable information leakage** in the public
coordination channel.  It does **not** provide formal differential privacy
guarantees.  The score is defined for an external observer who monitors ADMM
messages but has no access to internal solver state.

## Implementation

See `src/disclosure_metrics.py`.
