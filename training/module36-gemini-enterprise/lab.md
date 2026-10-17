---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 36: Designing an Enterprise Agent Strategy Challenge

## Goal

In this lab, you will design a strategy for a fictional company to adopt and govern a fleet of AI agents using Gemini Enterprise. This is a conceptual exercise to help you think about the challenges of managing agents at scale. **There is no coding in this lab.**

### Prerequisites
*   **Note on Costs:** Gemini Enterprise services can incur costs. Please be aware of the pricing for these services.

### The Scenario

You are the lead AI architect at a large retail company. The company wants to leverage AI agents across several departments: Sales, Marketing, and HR. Your task is to create a high-level plan for how you would use Gemini Enterprise to build, deploy, and govern these agents.

---

### Step 1: Identify the Agents

First, brainstorm the types of agents each department might need. Think about which ones you could build with the ADK, and which ones might be available as pre-built Google agents.

*   **Sales Team:**
    *   *Example Idea:* An ADK-built "Lead Qualifier Agent" that connects to Salesforce via a data connector to score new leads.
*   **Marketing Team:**
    *   *Example Idea:* Use the pre-built "Idea Generation Agent" for brainstorming new campaigns.
*   **HR Team:**
    *   *Example Idea:* An ADK-built "Policy Assistant Agent" that connects to the company's SharePoint to answer employee questions about HR policies.

**Your Task:** Come up with at least one more agent idea for each department.

---

### Step 2: Plan the Data Connectors

For your agents to be useful, they need access to the company's data.

**Your Task:** Based on the agents you identified above, list the Gemini Enterprise data connectors you would need to configure. For each connector, specify which agent would use it.
*   *Example:* **Salesforce Connector** for the `Lead Qualifier Agent`.

---

### Step 3: Design the Governance and Access Control

Not everyone should have access to every agent or every piece of data.

**Your Task:** Define a simple Role-Based Access Control (RBAC) policy.
*   Who should be able to **use** the `Lead Qualifier Agent`?
*   Who should be able to **edit or manage** the `Policy Assistant Agent`?
*   Should the `Marketing Team` be able to see data from the `Salesforce Connector`?

---

### Step 4: Plan for Monitoring and Cost Management

Finally, think about how you will monitor the system.

**Your Task:**
*   What is one key metric you would want to track for the `Lead Qualifier Agent`? (e.g., number of leads qualified per day).
*   What kind of alert would you set up for the `Policy Assistant Agent`? (e.g., alert if the agent fails to answer a question more than 10% of the time).
*   How would you set a budget for the Marketing team's usage of the "Idea Generation Agent"?

---

### Lab Summary

You have successfully created a high-level strategic plan for deploying and managing an enterprise-wide agent ecosystem.

You have learned to think about:
*   Identifying opportunities for specialized agents across a business.
*   The importance of data connectors for grounding agents in enterprise reality.
*   Designing governance and access control policies to ensure security.
*   Planning for monitoring, alerting, and cost management in a production environment.

Check the `lab-solution.md` to see example answers for this exercise.

### Self-Reflection Questions
- Why is a centralized "Agent Gallery" a valuable feature for a large enterprise? What problems does it solve?
- The "Agent Designer" is a no-code tool. What are the benefits of empowering non-developers to build their own simple agents, and what are the potential risks you would need to manage?
- How does grounding an agent in a private, enterprise data source (like SharePoint) using a secure data connector mitigate the risk of the agent hallucinating or providing incorrect information?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="36">

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

</SolutionVault>
