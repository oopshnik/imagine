from src.prompt_enhancer import enhance_prompt

import gradio as gr
import pollinations
import os
import tempfile
import traceback
import random

output_dir = os.path.join(tempfile.gettempdir(), "pollinations_output")
os.makedirs(output_dir, exist_ok=True)

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