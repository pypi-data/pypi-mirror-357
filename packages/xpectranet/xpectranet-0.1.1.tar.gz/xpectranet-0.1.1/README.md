# 🧠 XpectraNet SDK

> The XpectraNet® Protocol is the first symbolic infrastructure for mesh cognition — enabling agents to think, align, and evolve through canonical memory and remixable insight.

---

## Turn Any App Into a Cognitive Agent

**Symbolic memory. Diffused state. Mesh-aware remixing.**

XpectraNet is the memory and cognition layer for agents, apps, and LLMs — enabling symbolic understanding, protocol-driven alignment, and resumption across time and context.

---

## 🚀 Why XpectraNet?

- **Structured Symbolic Memory**  
  Every input is minted as a CognitiveMemoryBlock (CMB): intent, emotion, commitment, abstraction layer, and more.

- **Diffused State Reconstruction**  
  Instantly reconstructs protocol-grade cognitive context at any point — not just token replay.

- **Conflict & Drift Resolution**  
  Built-in protocols detect contradiction, clarify ambiguity, and realign cognition.

- **Mesh-Aware Remixing & Canonization**  
  Fork, remix, and canonize memory trails — making every reasoning step auditable and reusable.

**No re-architecture required. Plug XpectraNet into any agent, LLM, or workflow.**

---

## ⚡ Quick Start

```python
from xpectranet import mint, diffuse

# Mint a symbolic memory block from user input
cmb = mint("Where is my shipment?", role="user")

# Reconstruct protocol-level cognitive state
state = diffuse([], cmb)

print(state["intent"])      # → 'escalate'
print(state["emotion"])     # → 'concern'
print(state["commitment"])  # → 'resolve_delivery'
print(state["layer"])       # → 'L2'    # (Layer 2: Operations)
````

---

## 🛠️ Key SDK API

| Function                        | Purpose                                       |
|---------------------------------| --------------------------------------------- |
| `mint(text, role)`              | Mint a CognitiveMemoryBlock (CMB)             |
| `diffuse(trail, cmb)`           | Reconstruct current symbolic cognitive state  |
| `collapse(trail)`               | Detect & resolve contradiction in memory      |
| `clarify(trail)`                | Clarify ambiguity or drift in cognitive state |
| `remix(state, new_text, role)`  | Fork/remix new CMB from prior state           |
| `canonize(state)`               | Commit resolved state as immutable checkpoint |

---

## 🤖 Example: Customer Support Insight Trail

```python
from xpectranet import mint, diffuse

# Step 1: Capture a customer's issue as protocol insight
customer_issue = mint(
    "My order was supposed to arrive yesterday but hasn't shown up.",
    role="user"
)

# Step 2: Agent and system add protocol-grade events to the trail
trail = [
    customer_issue,
    mint("We're sorry for the delay. Let me check your order status.", role="agent"),
    mint("Order is delayed due to courier backlog. Estimated delivery: tomorrow.", role="system"),
    mint("Please notify the customer and offer a discount.", role="policy"),
    mint("Your order is scheduled for delivery tomorrow. As an apology, we've issued a discount.", role="agent"),
    mint("Thank you for the update and the discount.", role="user")
]

# Step 3: Reconstruct final symbolic state for audit and compliance
final_state = diffuse(trail, trail[-1])
print("Intent:", final_state["intent"])          # → 'resolve'
print("Commitment:", final_state["commitment"])  # → 'fulfill_order_and_compensate'
print("Emotion:", final_state["emotion"])        # → 'relieved'
print("Layer:", final_state["layer"])            # → 'L2'
```

---

## 🏆 Feature Highlights

* 🧠 **Structured Symbolic Memory:** Not just text — capture meaning, intention, and focus.
* 🔄 **Cognitive State Reconstruction:** True protocol context, not token lists.
* 🛡️ **Conflict & Drift Resolution:** Agents self-correct and align.
* 🔗 **Auditable Mesh Memory:** Every step is traceable, remixable, and canonizable.

---

## 🧪 Why Not Just Logs or Vectors?

| Capability                    | Logs & Vectors | XpectraNet SDK |
| ----------------------------- | :------------: | :------------: |
| Persistent state              |        ✅       |        ✅       |
| Symbolic tagging (intent etc) |        ❌       |        ✅       |
| Conflict/drift detection      |        ❌       |        ✅       |
| Protocol-driven correction    |        ❌       |        ✅       |
| Mesh-scale auditability       |        ❌       |        ✅       |

---

## 📚 Learn More

* [SDK Docs](https://xpectranet.com/sdk/docs)
* [Quick Start Guide](https://xpectranet.com/sdk/docs/quick_start)
* [Protocol Lifecycle](https://xpectranet.com/white-paper#section-5)
* [Audit & Replay Tutorial](https://xpectranet.com/sdk/docs/tutorials/how_to_audit_symbolic_memory.md)

---

## 🔐 License

Licensed under [BSL-1.1-XD](https://xpectranet.com/license).

* Free for non-commercial use.
* Commercial, SaaS, or forked use requires a paid protocol license.

© 2025 Xpectra Data Technologies Ltd.
*Symbolic Cognition. Protocol Memory. Mesh Intelligence.*

---