import gradio as gr
import pollinations
import time
import os
import tempfile
import asyncio
import traceback
import random

output_dir = os.path.join(tempfile.gettempdir(), "pollinations_output")
os.makedirs(output_dir, exist_ok=True)

async def enhance_prompt(prompt, style):
    if not prompt or not style:
        return prompt
    
    try:
        text_model = pollinations.Async.Text(model="llama", system="You are a creative assistant that enhances image prompts. Without comments")
        enhanced_prompt = await text_model(
            prompt=f"Enhance this prompt for an AI image generator: '{prompt}' Style: {style}. Make it detailed and vivid but keep it concise (max 100 words).",
            display=False,
            encode=True
        )
        
        if enhanced_prompt and hasattr(enhanced_prompt, 'response'):
            return enhanced_prompt.response.strip()
        return prompt
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        return prompt

async def generate_images(
    prompt: str,
    style: str,
    model: str,
    seed: int,
    width: int,
    height: int,
    enhance_prompt_checked: bool,
    enhance_image: bool,
    nologo: bool,
    private: bool,
    safe: bool,
    num_images: int
):
    if not prompt:
        raise gr.Error("Prompt cannot be empty.")
    
    
    # Enhance the prompt if requested
    working_prompt = prompt
    if enhance_prompt_checked and style:
        working_prompt = await enhance_prompt(prompt, style)
    
    image_paths = []
    errors = []
    
    for i in range(num_images):
        try:
            # Use the same seed for reproducibility, or increment it for variations
            effective_seed = int(seed)
            if effective_seed >= 0:
                current_seed = effective_seed + i
            else:
                # Generate an explicit random seed for each image if seed is -1
                current_seed = random.randint(0, 2147483647)
            
            image_model = pollinations.Async.Image(
                model=model,
                seed=current_seed,
                width=int(width),
                height=int(height),
                enhance=enhance_image,
                nologo=nologo,
                private=private,
                safe=safe,
                referrer="imagine"
            )
            
            # Modify prompt based on style if not using prompt enhancer
            styled_prompt = working_prompt
            if not enhance_prompt_checked and style and style != "None":
                if style == "Ghibli":
                    styled_prompt = f"{working_prompt}, Studio Ghibli style, hand-drawn animation, soft colors, whimsical"
                elif style == "Cyberpunk":
                    styled_prompt = f"{working_prompt}, cyberpunk style, neon colors, high-tech, dystopian, futuristic"
                elif style == "Realistic":
                    styled_prompt = f"{working_prompt}, photorealistic, detailed, 8k, professional photography"
                elif style == "Anime":
                    styled_prompt = f"{working_prompt}, anime style, vibrant colors, detailed line art, Japanese animation"
            
            image = await image_model(prompt=styled_prompt)
            
            if image is None or not hasattr(image, 'save'):
                response_content = getattr(image, 'response', None)
                errors.append(f"Image {i+1} generation failed: Invalid data from API")
                continue
                
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=output_dir) as tmpfile:
                output_path = tmpfile.name
                
            await image.save(file=output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                image_paths.append(output_path)
            else:
                size = os.path.getsize(output_path) if os.path.exists(output_path) else -1
                if os.path.exists(output_path):
                    try: os.remove(output_path)
                    except OSError: pass
                errors.append(f"Image {i+1} failed: Output file is missing or empty (size: {size})")
                
        except Exception as e:
            traceback.print_exc()
            errors.append(f"Image {i+1} error: {type(e).__name__}")
    
    if not image_paths and errors:
        raise gr.Error("\n".join(errors))
        
    # Return the generated images or empty placeholders if some failed
    # Return the list of image paths and the working prompt
    return image_paths, working_prompt

with gr.Blocks() as demo:
    gr.HTML("""
        <style>
            body, .gradio-container {
                font-family: "Montserrat", "Roboto", system-ui, sans-serif;
            }
            h1, h2, h3, button {
                font-family: "Montserrat", "Roboto", system-ui, sans-serif;
                font-weight: 600;
            }
            code, pre {
                font-family: "Cascadia Code", "Consolas", monospace;
            }
            .header-text {
                text-align: center;
                margin-bottom: 1rem;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            /* Mobile optimizations */
            @media (max-width: 768px) {
                .gradio-container {
                    padding: 10px !important;
                }
                .mobile-full-width {
                    width: 100% !important;
                }
            }
        </style>
        <div class="header-text">
            <h1>🌌 Imagine</h1>
            <p>AI Image Generation with FLUX Schnell & SDXL Turbo</p>
        </div>
    """)

    with gr.Row():
        prompt_input = gr.Textbox(
            placeholder="Describe the image you want to create...",
            lines=3,
            label="Prompt"
        )
    
    with gr.Row():
        with gr.Column(scale=1):
            style_select = gr.Dropdown(
                ["None", "Ghibli", "Cyberpunk", "Realistic", "Anime"],
                value="None",
                label="Style"
            )
        
        with gr.Column(scale=1):
            num_images_slider = gr.Slider(
                minimum=1,
                # Removed maximum limit
                step=1,
                value=1,
                label="Number of Images"
            )
    
    with gr.Row():
        with gr.Column(scale=2):
            run_button = gr.Button("Generate", variant="primary")
        
        with gr.Column(scale=1):
            enhance_prompt_check = gr.Checkbox(
                label="Use AI Prompt Enhancement",
                value=False
            )
    
    # Image output gallery
    image_gallery = gr.Gallery(label="Generated Images", show_label=True, elem_id="gallery")
    
    enhanced_prompt_output = gr.Textbox(label="Enhanced Prompt", visible=True, lines=3)
    
    with gr.Accordion("Advanced Settings", open=False):
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                model_select = gr.Radio(
                    ["flux", "turbo"],
                    label="Model",
                    value="flux",
                    info="FLUX Schnell or SDXL-Turbo"
                )
                
                seed_slider = gr.Slider(
                    minimum=-1,
                    maximum=2147483647,
                    step=1,
                    value=-1,
                    label="Seed",
                    info="-1 for random"
                )
            
            with gr.Column(scale=1):
                with gr.Row():
                    width_slider = gr.Slider(
                        minimum=256,
                        maximum=2048,
                        step=64,
                        value=1024,
                        label="Width"
                    )
                    height_slider = gr.Slider(
                        minimum=256,
                        maximum=2048,
                        step=64,
                        value=1024,
                        label="Height"
                    )
                
                with gr.Row():
                    enhance_image_check = gr.Checkbox(label="Enhance Image", value=False)
                    nologo_check = gr.Checkbox(label="No Logo", value=True)
                    private_check = gr.Checkbox(label="Private", value=True)
                    safe_check = gr.Checkbox(label="Safe Mode", value=False)

    gr.Examples(
        examples=[
            "A serene mountain lake with reflections of autumn trees",
            "A futuristic city with flying vehicles and holographic billboards",
            "A magical library with floating books and glowing orbs of light",
            "An underwater scene with bioluminescent creatures and coral",
            "A steampunk-inspired train station with brass mechanisms and steam",
        ],
        inputs=[prompt_input],
        label="Examples"
    )

    gr.HTML("""
        <div style="text-align: center; margin-top: 1rem; font-size: 0.8rem;">
            <p>Powered by <a href="https://pollinations.ai/" target="_blank">Pollinations.ai</a> | <a href="https://github.com/oopshnik/imagine" target="_blank">Source Code on GitHub</a></p>
        </div>
    """)

    # Define input/output relationship
    run_button.click(
        fn=generate_images,
        inputs=[
            prompt_input,
            style_select,
            model_select,
            seed_slider,
            width_slider,
            height_slider,
            enhance_prompt_check,
            enhance_image_check,
            nologo_check,
            private_check,
            safe_check,
            num_images_slider
        ],
        # Output to the gallery and the enhanced prompt textbox
        outputs=[
            image_gallery,
            enhanced_prompt_output
        ],
        api_name="generate"
    )

    # Make prompt enhancement visible when checkbox is clicked
    enhance_prompt_check.change(
        fn=lambda x: gr.update(visible=x),
        inputs=[enhance_prompt_check],
        outputs=[enhanced_prompt_output]
    )

if __name__ == "__main__":
    demo.launch()
