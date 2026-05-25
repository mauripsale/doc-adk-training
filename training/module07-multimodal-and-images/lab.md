---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 7: Building a Visual Product Catalog Analyzer

## Goal

In this lab, you will build a multimodal agent that can analyze a product image and generate a marketing description. This will teach you how to handle image inputs and perform programmatic execution with a vision-capable agent.

### The Architecture

You will use the **App and Runner** pattern you learned in Module 6 to build a Python script that:
1.  Loads local image files as `types.Part` objects.
2.  Constructs a multimodal prompt containing both text and image data.
3.  Executes the agent using `run_async`.

### Step 1: Create and Prepare the Project

1.  **Create the agent project:**
    ```shell
    adk create visual_catalog
    ```
2.  **Navigate into the new directory:**
    ```shell
    cd visual_catalog
    ```
3.  **Install Dependencies:**
    This lab requires the `Pillow` library for image handling.
    ```shell
    pip install Pillow
    ```
4.  **Set up your `.env` file.**
    Vision models require a Vertex AI configuration. Ensure your `.env` file looks like this:
    ```text
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT="your-project-id"
    GOOGLE_CLOUD_LOCATION="us-central1"
    ```

### Step 2: Implement the Multimodal Script

**Exercise:** Create a file named `main.py` in your `visual_catalog` directory. Your task is to complete the core logic inside the `analyze_product` method by filling in the `# TODO` sections.

> **Note on Sessions:** When using `run_async` programmatically, you must explicitly create a session in the runner's session service before sending a message, just as you did with `curl` in Module 5.

```python
import asyncio
import os
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

# Helper function to load an image from a local file path
def load_image_from_file(path: str) -> types.Part:
    """Load image from file and return a types.Part object."""
    with open(path, 'rb') as f:
        image_bytes = f.read()
    
    mime_type = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'

    return types.Part(
        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
    )

class VisualCatalogApp:
    def __init__(self):
        # 1. Define the Intelligence
        self.agent = LlmAgent(
            model='gemini-3.5-flash',
            name='catalog_writer',
            instruction="You are a professional product catalog writer. Analyze the image and write a compelling description."
        )
        # 2. Build the Infrastructure
        self.app = App(name="visual_catalog", root_agent=self.agent)
        self.runner = InMemoryRunner(app=self.app)

    async def analyze_product(self, product_id: str, image_path: str):
        print(f"\n--- Analyzing Product: {product_id} ---")
        user_id = "catalog_admin"
        session_id = f"sess_{product_id}"

        # TODO: 1. Create the session explicitly in the session service
        # Hint: Use self.runner.session_service.create_session(...)
        ...

        # TODO: 2. Load the image using the helper function
        image_part = ...

        # TODO: 3. Create the multimodal message (types.Content object)
        msg = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Analyze this image for product {product_id}."),
                image_part
            ]
        )

        # TODO: 4. Run the agent using run_async
        print("📸 Sending image to Gemini...")
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=msg
        ):
            if event.is_final_response():
                print(f"✅ Description:\n{event.content.parts[0].text}\n")

async def main():
    load_dotenv()
    catalog = VisualCatalogApp()

    # Images are expected to be in the parent directory for this lab
    products = [
        ('HEADPHONES-01', '../headphones.jpg'),
        ('LAPTOP-02', '../laptop.jpg'),
    ]

    for product_id, path in products:
        if os.path.exists(path):
            await catalog.analyze_product(product_id, path)
            await asyncio.sleep(1)
        else:
            print(f"⚠️ Image not found: {path}")

if __name__ == '__main__':
    asyncio.run(main())
```

### Lab Summary
You have successfully built a multimodal agent! You have learned:
*   How to package image bytes into a `types.Part` object.
*   The importance of explicitly creating a **Session** when using `run_async` programmatically.
*   How to construct a structured `types.Content` object for complex inputs.

### Self-Reflection Questions
- Why did we have to call `create_session` manually this time, whereas in Module 6's `run_debug` we didn't?
- How does the `InMemoryRunner` simplify the setup of the `SessionService` compared to a base `Runner`?
- If you wanted to analyze a PDF document instead of an image, which `mime_type` would you use in the `types.Blob`?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDctbXVsdGltb2RhbC1hbmQtaW1hZ2VzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module07-multimodal-and-images/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
