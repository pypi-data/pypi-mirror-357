import os
import logging

logger = logging.getLogger(__name__)


def get_prompts(config):
    """
    Load prompt templates from the configured prompt folder.
    
    Args:
        config: Configuration object containing prompt_folder path
        
    Returns:
        dict: Dictionary of prompt templates
    """
    directory_path = config.prompt_folder
    prompts = {}
    system_count = 0
    user_count = 0
    standard_count = 0
    
    try:
        # Check if directory exists
        if not os.path.exists(directory_path):
            logging.error(f"Prompt directory not found: {directory_path}")
            return prompts
            
        if not os.path.isdir(directory_path):
            logging.error(f"Prompt path is not a directory: {directory_path}")
            return prompts
            
        file_list = os.listdir(directory_path)
        logging.info(f"Found {len(file_list)} files in prompt directory")
        
        for filename in file_list:
            try:
                if not filename.endswith('.txt'):
                    logging.debug(f"Skipping non-txt file: {filename}")
                    continue
                    
                basename = filename.split('.')[0]
                file_path = os.path.join(directory_path, filename)
                
                # Check if file is readable
                if not os.access(file_path, os.R_OK):
                    logging.warning(f"Cannot read prompt file (permission denied): {file_path}")
                    continue
                
                with open(file_path, 'r') as file:
                    try:
                        content = file.read()
                        if not content.strip():
                            logging.warning(f"Empty prompt file: {file_path}")
                            continue
                            
                        if '.system.txt' in filename:
                            if basename not in prompts:
                                prompts[basename] = {}
                            prompts[basename]['system'] = content
                            system_count += 1
                            logging.debug(f"Loaded system prompt: {basename}")
                        elif '.user.txt' in filename:
                            if basename not in prompts:
                                prompts[basename] = {}
                            prompts[basename]['user'] = content
                            user_count += 1
                            logging.debug(f"Loaded user prompt: {basename}")
                        else:
                            prompts[basename] = content
                            standard_count += 1
                            logging.debug(f"Loaded standard prompt: {basename}")
                    except UnicodeDecodeError as e:
                        logging.error(f"Failed to decode file {file_path}: {str(e)}")
            except Exception as e:
                logging.error(f"Error processing prompt file {filename}: {str(e)}")
                
        logging.info(f"Loaded {len(prompts)} prompt templates (system: {system_count}, user: {user_count}, standard: {standard_count})")
        
        # Validate that prompts with 'system' also have 'user' parts
        for name, prompt in prompts.items():
            if isinstance(prompt, dict):
                if 'system' in prompt and 'user' not in prompt:
                    logging.warning(f"Prompt {name} has system part but missing user part")
                if 'user' in prompt and 'system' not in prompt:
                    logging.warning(f"Prompt {name} has user part but missing system part")
                    
    except Exception as e:
        logging.error(f"Failed to load prompts: {str(e)}")
        
    return prompts

def prompt_template(name, data):
    """
    Format a prompt template with the provided data.
    
    Args:
        name: Name of the prompt template
        data: Dictionary of variables to substitute in the template
        
    Returns:
        str: Formatted prompt text (for standard prompts)
        dict: Dictionary with 'system' and/or 'user' keys (for multi-part prompts)
        None: If prompt not found or formatting fails
    """
    # This assumes prompts is available - you'll need to decide how to access it
    # Option 1: Pass it as parameter
    # Option 2: Make this a method of a class that holds prompts
    # Option 3: Load prompts inside this function using config
    
    try:
        if name not in prompts:
            logger.error(f"Prompt '{name}' not found in available prompts.")
            return None
            
        prompt = prompts[name]
        if prompt is None:
            logger.error(f"Prompt '{name}' exists but is None.")
            return None
            
        # Handle dict-based prompts (system/user)
        if isinstance(prompt, dict):
            result = {}
            
            # Format system prompt if exists
            if 'system' in prompt and prompt['system']:
                try:
                    result['system'] = prompt['system'].format(**data)
                except KeyError as e:
                    logger.error(f"Missing data key for system prompt formatting: {e}")
                    return None
                    
            # Format user prompt if exists
            if 'user' in prompt and prompt['user']:
                try:
                    result['user'] = prompt['user'].format(**data)
                except KeyError as e:
                    logger.error(f"Missing data key for user prompt formatting: {e}")
                    return None
                    
            return result
            
        # Handle standard string prompts
        else:
            try:
                return prompt.format(**data)
            except KeyError as e:
                logger.error(f"Missing data key for prompt formatting: {e}")
                return None
                
    except Exception as e:
        logger.error(f"Error formatting prompt '{name}': {str(e)}")
        return None