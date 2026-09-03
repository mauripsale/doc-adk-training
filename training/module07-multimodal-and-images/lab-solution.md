---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 7 Solution: Building a Visual Product Catalog Analyzer

## Goal

This file contains the complete code for the `main.py` script in the Visual Product Catalog Analyzer lab, demonstrating how to explicitly manage sessions when using `run_async` for multimodal input.

### `visual_catalog/main.py`

```python
import asyncio
import logging
import os
from google.adk import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

# Optional: Suppress noisy ADK/httpx logs
logging.getLogger("google.adk").setLevel(logging.WARNING)

# Helper function to load an image from a local file path
def load_image_from_file(path: str) -> types.Part:
    """Load image from file and return a types.Part object."""
    with open(path, 'rb') as f:
        image_bytes = f.read()
    
    # Simple logic to determine mime type
    mime_type = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'

    return types.Part(
        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
    )

class VisualCatalogApp:
    def __init__(self):
        # 1. Define the Agent (The Intelligence)
        # Using the modern ADK 2.0 Agent class
        self.agent = Agent(
            model='gemini-3.5-flash',
            name='catalog_writer',
            instruction="""
                You are an expert product catalog writer. 
                Your task is to analyze the provided image and generate a compelling, 
                professional description for a web catalog. 
                Highlight the main features, materials, and potential use cases.
            """.strip()
        )
        # 2. Build the App and Runner (The Infrastructure)
        self.app = App(name="visual_catalog", root_agent=self.agent)
        self.runner = InMemoryRunner(app=self.app)

    async def analyze_product(self, product_id: str, image_path: str):
        print(f"\n--- Analyzing Product: {product_id} ---")
        user_id = "catalog_admin"
        session_id = f"sess_{product_id}"

        # Step 1: Explicitly create the session
        # For run_async, the session resource must exist before sending messages.
        await self.runner.session_service.create_session(
            app_name=self.app.name,
            user_id=user_id,
            session_id=session_id
        )

        # Step 2: Load the image using the helper
        image_part = load_image_from_file(image_path)

        # Step 3: Construct the multimodal Content object
        msg = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Analyze product ID '{product_id}' and write a catalog description."),
                image_part
            ]
        )

        # Step 4: Run the agent using run_async
        print("📸 Sending image to Gemini...")
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=msg
        ):
            # Step 5: Extract the final text response
            if event.is_final_response():
                description = event.content.parts[0].text
                print(f"✅ Description Generated:\n{description}\n")

async def main():
    load_dotenv()
    catalog = VisualCatalogApp()

    # Assumes images are in the parent directory relative to your terminal
    products = [
        ('HEADPHONES-01', '../headphones.jpg'),
        ('LAPTOP-02', '../laptop.jpg'),
    ]

    for product_id, path in products:
        if os.path.exists(path):
            await catalog.analyze_product(product_id, path)
            await asyncio.sleep(1) # Rate limit protection
        else:
            print(f"⚠️ Warning: Image not found at {path}")

if __name__ == '__main__':
    asyncio.run(main())
```

> **Cleanup:** Unlike other modules, this project lives directly inside `module07-multimodal-and-images/` (the actual course repo folder) rather than in a separate `adk-training` scratch directory. Once you're done, delete `visual_catalog/`, `.venv/`, `pyproject.toml`, and `uv.lock` from inside this module's folder so they don't accidentally get committed to the repo.

### Self-Reflection Answers

1.  **Why did we have to call `create_session` manually this time, whereas in Module 6's `run_debug` we didn't?**
    *   **Answer:** `run_debug` is a high-level helper method that automatically handles session creation. `run_async` is the production standard; it requires explicit session management, giving developers more control.

2.  **How does the `InMemoryRunner` simplify the setup compared to a base `Runner`?**
    *   **Answer:** The `InMemoryRunner` comes pre-bundled with an `InMemorySessionService` configured, so you don't have to manage the service object manually.

3.  **If you wanted to analyze a PDF document instead of an image, which `mime_type` would you use?**
    *   **Answer:** You would use `application/pdf`. The `Part` and `Blob` structure remains the same for all media types.
