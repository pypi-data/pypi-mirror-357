from transformers import AutoModelForCausalLM, AutoProcessor


def load_model(model_path, device, torch_dtype):
    """
    Loads pretrained florence-2 model saved on shared folder.
    model_path (str): The path to the pre-trained model directory
    device (torch.device): The device to which the model should be moved (e.g., 'cpu', 'cuda').
    torch_dtype (torch.dtype): The desired data type for the model's parameters (e.g., torch.float32, torch.float16).
    Returns:
    model (AutoModelForCausalLM): The loaded model ready for inference
    """
    return AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch_dtype, trust_remote_code=True
    ).to(device)


def load_processor(processor_path):
    """
    Loads a pre-trained processor from the specified path.
    Parameters:
    processor_path (str): The path to the pre-trained processor on our shared fs.
    processor (AutoProcessor): The loaded processor ready to use along with the model.
    """
    return AutoProcessor.from_pretrained(processor_path, trust_remote_code=True)


def get_caption(
    images, caption_mode, model, processor, device, torch_dtype, max_new_tokens
):
    """
    Generates captions for a list of images using a specified model and processor version of florence-2.
    Parameters:
    images (list): A list of images to be captioned.
    caption_mode (str): The mode of caption (caption, detailed_caption, more_detailed_caption)
    model (AutoModelForCausalLM): Florence 2 model
    processor (AutoProcessor): Florence 2 processor
    device (torch.device): The device on which the model and processor will run (e.g., 'cpu', 'cuda').
    torch_dtype (torch.dtype): The data type for the model's parameters (e.g., torch.float32, torch.float16).
    max_new_tokens (int): The maximum number of new tokens to generate for each caption.
    Returns:
    list: A list of parsed captions for each image, processed according to the specified caption mode.
    """
    prompts = [caption_mode] * len(images)
    inputs = processor(text=prompts, images=images, return_tensors="pt").to(
        device, torch_dtype
    )
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=max_new_tokens,
        early_stopping=False,
        do_sample=False,
        num_beams=3,
    )

    generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=False)
    parsed_answers = []
    for generated_text, image in zip(generated_texts, images):
        _, height, width = image.size()
        parsed_answers.append(
            processor.post_process_generation(
                generated_text, task=caption_mode, image_size=(width, height)
            )
        )
    return parsed_answers
