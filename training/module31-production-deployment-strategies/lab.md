---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 31: Choosing the Right Deployment Strategy Challenge

## Goal

In this lab, you will apply the decision framework from the theory section to a series of real-world scenarios. This is a conceptual exercise to help you develop the strategic thinking needed to choose the right deployment path for your agents. There is no coding in this lab.

### The Scenarios

For each of the following scenarios, read the description and decide which deployment platform is the best fit: **Cloud Run**, **Agent Runtime**, **GKE**, or **Custom Server on Cloud Run**.

Be prepared to justify your choice based on the key requirements of each scenario.

---

#### **Scenario 1: The Startup MVP**

*   **Company:** A small, venture-backed startup.
*   **Product:** A new AI-powered customer service chatbot for e-commerce sites.
*   **Key Requirements:**
    *   Get a working version deployed for a pilot customer by the end of the week.
    *   Keep infrastructure costs as low as possible.
    *   The development team has minimal DevOps experience.
    *   Standard security (HTTPS, basic protection) is sufficient for now.

**Your Task:** Which platform should they choose and why?

---

#### **Scenario 2: The Government Contractor**

*   **Company:** A large defense and technology contractor.
*   **Product:** An internal agent that helps employees search through sensitive but unclassified government compliance documents.
*   **Key Requirements:**
    *   The system **must** be FedRAMP compliant.
    *   All access must be strictly controlled and auditable.
    *   The infrastructure must be fully managed to reduce the internal operational burden.

**Your Task:** Which platform is the only viable choice here, and why?

---

#### **Scenario 3: The FinTech Enterprise**

*   **Company:** A large financial services company with a mature IT department.
*   **Product:** A complex system of microservice agents for financial analysis that need to communicate with each other over a private network.
*   **Key Requirements:**
    *   The entire system must be deployed within the company's existing Kubernetes ecosystem.
    *   The security team requires fine-grained network policies to control traffic between agent services.
    *   Some analysis agents require access to GPU nodes for performance.

**Your Task:** Which platform should they use, and what are the trade-offs?

---

#### **Scenario 4: The University Integration**

*   **Company:** A university's IT department.
*   **Product:** An agent that allows students to ask questions about course availability.
*   **Key Requirements:**
    *   The agent must authenticate users against the university's central **LDAP** directory.
    *   The platform should still be serverless and cost-effective.

**Your Task:** Which hybrid approach is necessary here, and why?

---
sidebar_position: 2

### Lab Summary

You have now practiced applying a strategic framework to real-world deployment decisions. You have learned to:
*   Analyze business and technical requirements to choose a deployment platform.
*   Prioritize factors like speed, cost, compliance, and control.
*   Understand the specific use cases for Cloud Run, Agent Runtime, GKE, and custom server deployments.

Check the `lab-solution.md` to see the recommended answers for each scenario.

### Self-Reflection Questions
- For the Startup MVP, what are the potential downsides of choosing Cloud Run? At what point might they need to consider migrating to a different platform like GKE?
- Why is a "platform-first" security model, where you rely on the deployment environment for features like authentication and DDoS protection, generally a better approach than trying to build these features into your agent application code?
- If a new compliance requirement (e.g., PCI for handling credit card data) was introduced, how would that influence your choice of deployment platform?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzEtcHJvZHVjdGlvbi1kZXBsb3ltZW50LXN0cmF0ZWdpZXMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module31-production-deployment-strategies/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
