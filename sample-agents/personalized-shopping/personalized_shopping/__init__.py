# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import google.auth

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

import torch

# Workaround to Resolve the PyTorch-Streamlit Incompatibility Issue
torch.classes.__path__ = []

# Initialize webshop environment (requires Java)
# If Java is not available (e.g., in CI), set webshop_env to None
try:
    from .shared_libraries.init_env import init_env, webshop_env
except Exception:
    webshop_env = None
    init_env = None

from . import agent
