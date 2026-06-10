---
sidebar_position: 7
title: "Module 7: Multimodal and Image Processing"
---

# Module 7: Multimodal and Image Processing

## Theory

### Why Multimodal Matters

Many real-world applications require agents to understand and process more than just text. **Multimodal models**, like Gemini, can process text and images together, enabling a powerful new class of vision-enabled agents.

**Benefits**:

*   👁️ **Vision Understanding**: Analyze images to extract information, identify objects, and understand visual context.
*   🎨 **Image Generation**: Create new images from text descriptions.
*   🧠 **Multimodal Reasoning**: Combine visual and textual information to answer complex questions.
*   📄 **Document Analysis**: Extract text and structure from images of documents (OCR).

### The `types.Part` Object

The fundamental building block for multimodal content in the ADK is the `types.Part` object from the `google.genai` library. A user's prompt is no longer just a string, but a list of `Part` objects.

A `Part` can contain:
*   **Text:** `types.Part.from_text("Describe this image")`
*   **Image Data:** `types.Part(inline_data=types.Blob(data=image_bytes, mime_type='image/png'))`

When you send a list of these parts to a vision-capable model like `gemini-3.5-flash`, the model can reason about the text and the image(s) together.

#### Example: Building a Vision Agent
To send an image to an agent programmatically, you package it into a list and run it via an `App`:

```python
from google.adk import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

# 1. Define the agent
agent = Agent(
    name="vision_expert",
    model="gemini-3.5-flash",
    instruction="Describe the provided image in detail."
)

# 2. Wrap in an App
app = App(name="vision_app", root_agent=agent)
runner = InMemoryRunner(app=app)

# 3. Construct the multimodal list
multimodal_prompt = [
    "What is in this picture?",
    types.Part(inline_data=types.Blob(data=image_bytes, mime_type="image/jpeg"))
]

# 4. Run!
# response = await runner.run_debug(multimodal_prompt)
```

### Image Generation

Beyond understanding images, some models can also **generate** them. Services like **Agent Platform Imagen** provide text-to-image capabilities. You can create a custom tool that takes a text description, calls the image generation API, and returns the resulting image.

This allows you to build agents that can:
*   Create product mockups from a description.
*   Generate illustrations for a story.
*   Create charts and diagrams from data.

In the lab, you will build a "Visual Product Catalog Analyzer" that uses a single, vision-capable agent to analyze a product image and generate a marketing description from that analysis.

### Key Takeaways
- Multimodal models like Gemini can process text and images together, enabling vision-enabled agents.
- The `google.genai.types.Part` object is the building block for multimodal content, allowing you to combine text and image data in a single prompt.
- Vision-capable agents can be used for a wide range of tasks, including image analysis, document understanding, and multimodal reasoning.
- You can create custom tools to integrate with image generation services like Agent Platform Imagen.
