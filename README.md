# Imagine: AI Image Generation

A simple Gradio web app to generate images using AI models via Pollinations.ai. Supports models like FLUX Schnell and SDXL-Turbo.

## Features

- **Text-to-Image:** Generate images from text.
- **Model Selection:** Choose between `'flux'` (FLUX Schnell) and `'turbo'` (SDXL-Turbo).
- **Style Presets:** Ghibli, Cyberpunk, Realistic, Anime.
- **Prompt Enhancement:** Improve prompt clarity using LLaMA.
- **Custom Options:** 
  - Set width, height, seed, number of outputs
  - Enable private generation
  - Toggle safe mode
  - Remove watermarks/logos
  - Enhance image quality
- **Web UI:** Built with Gradio.
- **Examples Included:** Get started fast.

## Requirements

- Python 3.11+
- Install dependencies:
  ```
  pip install gradio pollinations
  ```

## Installation

```
git clone https://github.com/oopshnik/imagine.git
cd imagine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install gradio pollinations
```

## Usage

```
python main.py
```

Open the URL shown in the terminal (usually `http://127.0.0.1:7860`) in your browser.  
Enter a prompt, choose options, and click **Generate**.

## Contributing

GitHub repo: https://github.com/oopshnik/imagine


