---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 7 Solution: Building a Visual Product Catalog Analyzer

## Goal

This file contains the complete code for the `agent.py` script in the Visual Product Catalog Analyzer lab, refactored to use a single agent and the standard `Runner`.

### `visual_catalog/agent.py`

```python
"""
Visual Product Catalog Analyzer
Analyzes product images and generates descriptions using a single agent.
"""

import asyncio
import os
from typing import List, Dict
from google.adk.agents import Agent
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import Session, InMemorySessionService
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
            model='gemini-2.5-flash',
            name='catalog_agent',
            instruction="""
You are an expert product catalog writer.
Your task is to analyze the provided product image and write a compelling, professional, marketing-ready description for it.
Describe the product type, key visual features (like color, material, and design), and any visible text.
            """.strip(),
        )
        self.session_service = InMemorySessionService()
        self.runner = Runner(session_service=self.session_service)

    async def analyze_product(self, product_id: str, image_path: str):
        """Analyze a product image and create a catalog entry."""
        print(f"\n--- Analyzing Product: {product_id} ---")

        # Create a new session for this specific analysis
        session = await self.session_service.create_session(
            app_name="visual_catalog", user_id=f"user_{product_id}"
        )

        # Step 1: Load the image
        image_part = load_image_from_file(image_path)

        # Step 2: Create the multimodal prompt
        analysis_query = [
            types.Part.from_text(
                f"Analyze this product image for '{product_id}' and write a marketing description."
            ),
            image_part
        ]

        # Step 3: Run the agent to get the catalog entry in one step
        print("📸📝 Analyzing image and generating catalog entry...")
        analysis_result = await self.runner.run_async(
            session=session,
            new_message=analysis_query,
            agent=self.catalog_agent
        )
        catalog_text = analysis_result.content.parts[0].text
        print(f"✅ Catalog Entry Generated:\n{catalog_text}\n")

        self.catalog.append({'product_id': product_id, 'catalog_entry': catalog_text})

async def main():
    """Main entry point to run a demo."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    analyzer = ProductCatalogAnalyzer()

    # Use local images directly
    products = [
        ('PROD-001', '../../headphones.jpg'),
        ('PROD-002', '../../laptop.jpg'),
    ]

    # Batch analyze the products
    for product_id, image_path in products:
        await analyzer.analyze_product(product_id, image_path)
        await asyncio.sleep(1) # To avoid hitting rate limits

if __name__ == '__main__':
    asyncio.run(main())
```
