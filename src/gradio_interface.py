import gradio as gr
from src.image_generator import generate_images

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
            <h1>🚀 Imagine</h1>
            <p>Advacned AI Image Generation with FLUX Schnell & SDXL Turbo</p>
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
    
    enhanced_prompt_output = gr.Textbox(label="Enhanced Prompt", visible=False, lines=3)
    
    with gr.Accordion("Advanced Settings", open=False):
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                model_select = gr.Radio(
                    ["flux", "turbo"],
                    label="Model",
                    value="flux",
                    info="Flux Schnell or SDXL-Turbo"
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
            <p>Powered by <a href="https://pollinations.ai/" target="_blank">Pollinations.ai</a> / <a href="https://github.com/oopshnik/imagine" target="_blank">Source Code</a> / <a href="https://t.me/imag1ne_bot target="_blank>Telegram Bot (Mini App)</a>

            </p>
            
            
            
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