---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 31 Solution: Choosing the Right Deployment Strategy

## Goal

This file contains the recommended solutions and reasoning for the scenario-based exercise in the lab.

---

#### **Scenario 1: The Startup MVP**

*   **Recommendation:** ✅ **Cloud Run**
*   **Justification:** This scenario is the primary use case for Cloud Run. The key drivers are **speed** and **low cost**. The `adk deploy cloud_run` command allows the team to deploy in minutes without any DevOps expertise. The serverless, pay-per-use model is perfect for a startup managing its burn rate, and the platform's automatic security (HTTPS, DDoS, IAM) is more than sufficient for an MVP.

---

#### **Scenario 2: The Government Contractor**

*   **Recommendation:** ✅✅ **Agent Engine**
*   **Justification:** The non-negotiable requirement is **FedRAMP compliance**. Agent Engine is the only platform listed that provides this out of the box as a managed service. This eliminates a massive amount of complex and expensive compliance work the contractor would otherwise have to do themselves. The automatic audit logging and sandboxed execution are also critical features for this use case.

---

#### **Scenario 3: The FinTech Enterprise**

*   **Recommendation:** ✅ **GKE (Google Kubernetes Engine)**
*   **Justification:** The company already has a significant investment in Kubernetes. The requirements for **full control over the network** (via NetworkPolicies) and **custom hardware** (GPUs) are classic drivers for choosing Kubernetes over a more abstracted serverless platform. While GKE has a higher operational cost and complexity, it provides the flexibility and control this enterprise requires for its complex, high-performance computing environment.

---

#### **Scenario 4: The University Integration**

*   **Recommendation:** ⚙️ **Custom Server on Cloud Run**
*   **Justification:** The key requirement is **custom authentication (LDAP)**, which is not natively supported by Cloud Run's IAM or Agent Engine's OAuth. This forces the team to build a custom FastAPI server where they can implement their own LDAP authentication middleware. However, they still want a serverless, cost-effective platform. The best solution is to deploy this custom server to **Cloud Run**. This gives them the platform benefits of serverless scaling and management while allowing for the specific application-level authentication logic they need.

### Self-Reflection Answers

1.  **For the Startup MVP, what are the potential downsides of choosing Cloud Run? At what point might they need to consider migrating to a different platform like GKE?**
    *   **Answer:** While ideal for MVPs, Cloud Run's potential downsides include **cold start latency** (agents take time to spin up after periods of inactivity) and **limited network control** compared to Kubernetes. A migration to GKE should be considered when the system evolves into a complex microservices architecture requiring private networking, critical performance that cannot tolerate cold starts, or specialized hardware like GPUs that are more easily managed in a Kubernetes cluster.

2.  **Why is a "platform-first" security model, where you rely on the deployment environment for features like authentication and DDoS protection, generally a better approach than trying to build these features into your agent application code?**
    *   **Answer:** A "platform-first" security model is superior because it reduces operational overhead by offloading complex and critical tasks (like TLS certificate rotation, DDoS protection, and IAM authentication) to the platform. This leverages the robust, battle-tested, and often certified security features of the cloud provider, ensuring a consistent and auditable security posture across all services while minimizing the risk of human error in application-level code. Building these features into your application code is time-consuming, error-prone, and rarely matches the robustness of platform-level security.

3.  **If a new compliance requirement (e.g., PCI for handling credit card data) was introduced, how would that influence your choice of deployment platform?**
    *   **Answer:** A new compliance requirement like PCI would heavily influence the deployment choice. While platforms like GKE and Cloud Run can be made PCI compliant, the burden of implementing and maintaining all necessary controls (e.g., encryption, access controls, audit trails, network segmentation) falls heavily on the development team. If an existing managed platform like Agent Engine (or a specialized PCI-compliant service) were certified for the specific compliance standard, it would be the simplest choice as the compliance is built-in. In the absence of a certified managed platform, the decision would also depend on whether the agent itself handles sensitive data; a common pattern is to delegate responsibility for sensitive data to a separate, already-compliant service.
