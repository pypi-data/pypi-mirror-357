import torch
from diffusers import StableDiffusionPipeline

def TTI(prompt, output_path="output_cpu.png"):
    # Load model in CPU mode with low RAM usage
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        revision="fp16",  # loads fp16 weights but on CPU will be converted back to fp32
        torch_dtype=torch.float32,
        use_auth_token=True  # if needed; remove if not
    )
    pipe = pipe.to("cpu")

    # Reduce steps for faster generation (default is 50)
    image = pipe(prompt, num_inference_steps=15).images[0]

    image.save(output_path)
    print(f"Image saved to {output_path}")

if __name__ == "__main__":
    prompt = "A cozy cabin in the snowy mountains"
    text_to_image_cpu(prompt)
