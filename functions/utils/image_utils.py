import cv2
import numpy as np
import base64

def decode_base64_image(base64_str: str) -> np.ndarray:
    """
    Decodes a base64 encoded image string into an OpenCV numpy array (BGR).
    
    Args:
        base64_str (str): Base64 encoded image string.
        
    Returns:
        np.ndarray: OpenCV BGR image matrix.
        
    Raises:
        ValueError: If the base64 string is invalid or cannot be decoded.
    """
    try:
        # Remove "data:image/...;base64," header if present
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]
            
        img_data = base64.b64decode(base64_str)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image from base64 string.")
            
        return img
    except Exception as e:
        raise ValueError(f"Invalid base64 image data: {str(e)}")

def validate_image(img: np.ndarray) -> bool:
    """
    Validates if the image is suitable for processing.
    
    Args:
        img (np.ndarray): OpenCV image matrix.
        
    Returns:
        bool: True if image is valid, False otherwise.
    """
    if img is None:
        return False
        
    # Check minimum dimensions (100x100)
    height, width = img.shape[:2]
    if height < 100 or width < 100:
        return False
        
    return True
