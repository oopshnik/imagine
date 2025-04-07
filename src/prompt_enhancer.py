import pollinations

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