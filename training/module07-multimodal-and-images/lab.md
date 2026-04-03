---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 7: Building a Visual Product Catalog Analyzer Challenge

## Goal

In this lab, you will build a multimodal agent that can analyze a product image and generate a marketing description. This will teach you how to handle image inputs and perform a multi-step reasoning process with a single, vision-capable agent.

### The Architecture

You will build a single `LlmAgent` that can:
1.  Receive a prompt containing both an image and a text instruction.
2.  Analyze the visual features of the image.
3.  Use that analysis to generate a polished, marketing-ready product description based on the initial instruction.

### Step 1: Create and Prepare the Project

1.  **Create the agent project:**
    ```shell
    adk create visual_catalog
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd visual_catalog
    ```

3.  **Install Dependencies:**
    This lab requires the `Pillow` library for image handling. Install it now:
    ```shell
    pip install Pillow
    ```

4.  **Set up your `.env` file.**
    Create a `.env` file in this directory. Vision models require a Vertex AI configuration.
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```

### Step 2: Implement the Multimodal Agent

**Exercise:** Open `agent.py`. The full boilerplate code is provided below. Your task is to complete the core logic inside the `analyze_product` method by filling in the `# TODO` sections.

```python
# In agent.py (Starter Code)
import asyncio
import os
from typing import List, Dict
from google.adk.agents import Agent
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import Session, InMemorySessionService # Import services
import io

# Helper function to load an image from a local file path
def load_image_from_file(path: str) -> types.Part:
    """Load image from file and return a types.Part object."""
    with open(path, 'rb') as f:
        image_bytes = f.read()
    
    if path.lower().endswith('.png'):
        mime_type = 'image/png'
    elif path.lower().endswith(('.jpg', '.jpeg')):
        mime_type = 'image/jpeg'
    else:
        mime_type = 'image/jpeg' # Default

    return types.Part(
        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
    )

class ProductCatalogAnalyzer:
    """Analyze product images and create catalog entries."""

    def __init__(self):
        """Initialize product catalog analyzer."""
        self.catalog: List[Dict] = []
        self.catalog_agent = Agent(
            model='gemini-2.5-flash', name='catalog_agent',
            instruction="You are a product catalog writer. Analyze the provided image and generate a compelling marketing description."
        )
        # Create the session service and the runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(session_service=self.session_service)

    async def analyze_product(self, product_id: str, image_path: str):
        """Analyze a product image and create a catalog entry."""
        print(f"\n--- Analyzing Product: {product_id} ---")


        # TODO: 1. Create a new session for this analysis.
        # Use `self.session_service.create_session`, providing an `app_name`
        # (e.g., "visual_catalog") and a `user_id`.
        session = None # Replace this

        # TODO: 2. Call the `load_image_from_file` helper to get the `image_part`.
        image_part = None # Replace this

        # TODO: 3. Create the `analysis_query`, which must be a list containing
        # a text part (e.g., "Analyze this image and write a marketing description.")
        # and the `image_part`.
        analysis_query = [] # Replace this

        # TODO: 4. Call the `catalog_agent` by using `self.runner.run_async`.
        # You must pass the `session` object, the `analysis_query` as the `new_message`,
        # and the `catalog_agent` as the `agent`.
        analysis_result = await self.runner.run_async(...) # Replace this
        catalog_text = analysis_result.content.parts[0].text
        print(f"✅ Catalog Entry Generated:\n{catalog_text}\n")

        self.catalog.append({'product_id': product_id, 'catalog_entry': catalog_text})

async def main():
    """Main entry point to run a demo."""
    from dotenv import load_dotenv
    load_dotenv()

    analyzer = ProductCatalogAnalyzer()

    # Use local images directly
    products = [
        ('PROD-001', '../../headphones.jpg'),
        ('PROD-002', '../../laptop.jpg'),
    ]

    for product_id, image_path in products:
        await analyzer.analyze_product(product_id, image_path)
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
```

### Step 3: Run and Test the Vision Agent

1.  **Run the agent script directly** after completing the `TODO`s.
    ```shell
    python agent.py
    ```
2.  **Analyze the Output:** You should see the script use the local images and then print the final marketing copy generated by the agent for each product.

### Having Trouble?
If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary
You have successfully built a multimodal agent that can see and understand images! You have learned to:
*   Create multimodal prompts by combining text and image `types.Part` objects.
*   Correctly initialize a `Runner` with a `SessionService` for programmatic execution.
*   Build a single agent that can perform a multi-step task: analyzing an image and then generating creative text based on that analysis.

### Self-Reflection Questions
- What are the benefits of using a single agent for this task versus the previous two-agent approach? What are the potential downsides?
- The `load_image_from_file` helper function reads the image as bytes. Why is it necessary to also provide a `mime_type` (like 'image/jpeg') when creating the `types.Part` object?
- How could you extend this project to handle video input? What kind of new agent or tool would you need to build?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDctbXVsdGltb2RhbC1hbmQtaW1hZ2VzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module07-multimodal-and-images/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
