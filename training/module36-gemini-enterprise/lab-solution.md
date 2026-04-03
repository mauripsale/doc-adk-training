---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 36 Solution: Designing an Enterprise Agent Strategy

## Goal

This file contains example answers and thought processes for the conceptual lab exercise on designing an enterprise agent strategy.

---

### Step 1: Identify the Agents (Example Ideas)

*   **Sales Team:**
    *   **Lead Qualifier Agent (ADK-built):** Connects to Salesforce to score new leads based on company size, industry, and budget.
    *   **Proposal Writer Agent (Agent Designer):** A no-code agent for the sales team to quickly generate standard sales proposals by filling in a few fields.

*   **Marketing Team:**
    *   **Idea Generation Agent (Pre-built):** Used for brainstorming new campaign slogans and themes.
    *   **Social Media Scheduler (ADK-built):** An agent that can draft and schedule social media posts, possibly connecting to a service like HubSpot.

*   **HR Team:**
    *   **Policy Assistant Agent (ADK-built):** Connects to the company's SharePoint to answer employee questions about HR policies.
    *   **Resume Screener (ADK-built):** An agent that can review resumes (PDF artifacts) and check them against a job description to provide a shortlist.

---

### Step 2: Plan the Data Connectors (Example Plan)

*   **Salesforce Connector:** Used by the `Lead Qualifier Agent` to access lead and account data.
*   **SharePoint Connector:** Used by the `Policy Assistant Agent` to access HR policy documents.
*   **Google Drive Connector:** Used by the `Resume Screener` to access resumes stored in a specific folder.
*   **HubSpot Connector:** Used by the `Social Media Scheduler` to post content.

---

### Step 3: Design the Governance and Access Control (Example Policy)

*   **`Lead Qualifier Agent`:**
    *   **Users:** `sales-team@company.com` group.
    *   **Managers:** `sales-managers@company.com` group (can view metrics and edit the agent).
*   **`Policy Assistant Agent`:**
    *   **Users:** All employees (`all-employees@company.com`).
    *   **Managers:** `hr-team@company.com`.
*   **Data Access:**
    *   The `Marketing Team` should **not** have direct access to the `Salesforce Connector`. If they need sales data, they should ask the `Lead Qualifier Agent`, which can provide summarized, non-sensitive information. This enforces a layer of abstraction and security.

---

### Step 4: Plan for Monitoring and Cost Management (Example Plan)

*   **`Lead Qualifier Agent` Metric:**
    *   **Key Metric:** "Lead Conversion Rate from Agent-Qualified Leads". This business-level metric measures the actual impact of the agent, not just its activity.
*   **`Policy Assistant Agent` Alert:**
    *   **Alert:** Set up an alert in Cloud Monitoring that triggers if the agent's "failure rate" (the percentage of queries where it couldn't find an answer) exceeds 15% over a 1-hour period. This could indicate a problem with the SharePoint connector or that the knowledge base is missing critical documents.
*   **Marketing Team Budget:**
    *   In Gemini Enterprise's cost management dashboard, create a budget for the "Marketing" cost center. Set a monthly limit of $500. Configure an alert to notify the `marketing-manager@company.com` when usage reaches 80% of the budget.

### Self-Reflection Answers

1.  **Why is a centralized "Agent Gallery" a valuable feature for a large enterprise? What problems does it solve?**
    *   **Answer:** A centralized "Agent Gallery" is invaluable for large enterprises as it solves key problems:
        *   **Discovery:** It prevents duplication of effort by allowing teams to easily find and understand existing agents that might already address their needs.
        *   **Sharing & Reusability:** It provides a formal and secure way to publish agents across the organization, promoting reuse of valuable agentic capabilities and accelerating development.
        *   **Adoption:** By making agents easily discoverable and accessible, it promotes the use of AI automation and fosters a culture of innovation within the enterprise.
        *   **Governance:** It provides a central point for managing agent lifecycle, versioning, and approval processes.

2.  **The "Agent Designer" is a no-code tool. What are the benefits of empowering non-developers to build their own simple agents, and what are the potential risks you would need to manage?**
    *   **Answer:**
        *   **Benefits:** Empowers business users (non-developers) to quickly automate simple tasks, fostering innovation and freeing up AI engineers for more complex projects. It democratizes agent creation and accelerates business process improvements.
        *   **Potential Risks:**
            *   **Reliability:** Non-developers might not implement proper guardrails or constraints, leading to unreliable or unpredictable agent behavior.
            *   **Cost Management:** Inefficient LLM calls due to poorly designed prompts or unnecessary tool usage can lead to increased costs.
            *   **Governance & Shadow IT:** Without proper oversight, it can lead to a proliferation of unmanaged agents (shadow IT) that pose security or compliance risks. Rigorous monitoring and governance are essential to mitigate these risks.
            *   **Security:** Users might inadvertently expose sensitive data if not properly trained on data handling and privacy.

3.  **How does grounding an agent in a private, enterprise data source (like SharePoint) using a secure data connector mitigate the risk of the agent hallucinating or providing incorrect information?**
    *   **Answer:** Grounding an agent in private, secure enterprise data sources (via Data Connectors) is the most effective method to mitigate hallucination and ensure accuracy. This approach leverages **Retrieval Augmented Generation (RAG)**, forcing the LLM to base its responses on retrieved, up-to-date, and approved company information from sources like SharePoint, Google Drive, or Salesforce, rather than relying solely on its static pre-trained knowledge. By providing specific, relevant context at inference time, it drastically reduces the risk of the agent fabricating information and ensures that responses are accurate, relevant, and secure according to enterprise standards.
