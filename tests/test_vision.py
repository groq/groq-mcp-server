import pytest
from pathlib import Path
import json
from src.groq_vision import analyze_image, analyze_image_json
from src.utils import MCPError

@pytest.mark.unit
def test_analyze_image(temp_dir, mock_groq_api_key, mock_httpx_client, sample_image_file):
    """Test basic image analysis"""
    result = analyze_image(
        input_file_path=str(sample_image_file),
        prompt="What's in this image?",
        output_directory=str(temp_dir)
    )
    
    # Test response structure
    assert result.type == "text"
    assert "Success" in result.text
    assert "saved as:" in result.text
    assert "Model used:" in result.text
    
    # Extract and read the output file
    output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
    assert output_file.exists()
    with open(output_file) as f:
        content = f.read()
    
    # Test content without being too rigid
    assert any(color in content.lower() for color in ["red", "black"])
    assert any(shape in content.lower() for shape in ["square", "rectangle"])
    assert any(pos in content.lower() for pos in ["center", "middle", "position"])

@pytest.mark.unit
def test_analyze_image_json(temp_dir, mock_groq_api_key, mock_httpx_client, sample_image_file):
    """Test JSON-formatted image analysis"""
    result = analyze_image_json(
        input_file_path=str(sample_image_file),
        prompt="Extract key information from this image as JSON",
        output_directory=str(temp_dir)
    )
    
    # Test response structure
    assert result.type == "text"
    assert "Success" in result.text
    assert "saved as:" in result.text
    assert "Model used:" in result.text
    
    # Extract and read the output file
    output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
    assert output_file.exists()
    with open(output_file) as f:
        content = json.load(f)
    
    # Test JSON structure without being too rigid
    assert isinstance(content, (dict, list))
    
    # Helper function to check content recursively
    def check_content(obj):
        if isinstance(obj, dict):
            return any(check_content(v) for v in obj.values())
        elif isinstance(obj, list):
            return any(check_content(item) for item in obj)
        elif isinstance(obj, str):
            return (
                any(color in obj.lower() for color in ["red", "black"]) or
                any(shape in obj.lower() for shape in ["square", "rectangle"]) or
                any(pos in obj.lower() for pos in ["center", "middle", "position"])
            )
        return False
    
    assert check_content(content), "JSON response should contain image description elements"

@pytest.mark.unit
def test_invalid_image_file(temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test that invalid image file raises error"""
    with pytest.raises(MCPError):
        analyze_image(
            input_file_path="nonexistent.jpg",
            output_directory=str(temp_dir)
        )

@pytest.mark.unit
def test_invalid_prompt(temp_dir, mock_groq_api_key, mock_httpx_client, sample_image_file):
    """Test that empty prompt raises error"""
    with pytest.raises(MCPError, match="Prompt is required"):
        analyze_image(
            input_file_path=str(sample_image_file),
            prompt="",
            output_directory=str(temp_dir)
        )

@pytest.mark.parametrize("temperature", [-1.0, 2.1])
@pytest.mark.unit
def test_invalid_temperature(temp_dir, mock_groq_api_key, mock_httpx_client, sample_image_file, temperature):
    """Test that invalid temperature raises error"""
    with pytest.raises(MCPError):
        analyze_image(
            input_file_path=str(sample_image_file),
            temperature=temperature,
            output_directory=str(temp_dir)
        )

@pytest.mark.integration
def test_analyze_image_integration(temp_dir, mock_groq_api_key, sample_image_file):
    """Integration test for image analysis"""
    result = analyze_image(
        input_file_path=str(sample_image_file),
        prompt="Please describe this image, including its colors, shapes, and composition.",  # More specific prompt
        output_directory=str(temp_dir)
    )
    
    # Test response structure
    assert result.type == "text"
    assert "Success" in result.text
    assert "saved as:" in result.text
    assert "Model used:" in result.text
    
    # Extract and read the output file
    output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
    assert output_file.exists()
    with open(output_file) as f:
        content = f.read().lower()  # Convert to lowercase once
    
    # Test content with more flexible criteria
    # 1. Check if response is substantial
    assert len(content) > 50, "Response is too short"
    
    # 2. Check if it contains descriptive language
    descriptive_terms = [
        # Colors (more general)
        "color", "colored", "dark", "light", "bright", "shade",
        # Shapes (more general)
        "shape", "geometric", "form", "figure",
        # Position/Composition (more general)
        "position", "located", "placed", "composition", "background", "foreground",
        # Common descriptive words
        "appears", "contains", "shows", "depicts", "image", "picture"
    ]
    
    matches = [term for term in descriptive_terms if term in content]
    assert len(matches) >= 3, f"Response lacks descriptive terms. Found only: {matches}"
    
    # 3. Check for basic English structure
    basic_words = ["the", "is", "are", "in", "on", "with", "and"]
    assert any(word in content for word in basic_words), "Response may not be well-formed English"

@pytest.mark.integration
def test_analyze_image_json_integration(temp_dir, mock_groq_api_key, sample_image_file):
    """Integration test for JSON-formatted image analysis"""
    result = analyze_image_json(
        input_file_path=str(sample_image_file),
        prompt="Extract key information from this image as JSON",
        output_directory=str(temp_dir)
    )
    
    # Test response structure
    assert result.type == "text"
    assert "Success" in result.text
    assert "saved as:" in result.text
    assert "Model used:" in result.text
    
    # Extract and read the output file
    output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
    assert output_file.exists()
    with open(output_file) as f:
        content = json.load(f)
    
    # Test JSON structure without being too rigid
    assert isinstance(content, (dict, list))
    
    # Use the same helper function from unit test
    def check_content(obj):
        if isinstance(obj, dict):
            return any(check_content(v) for v in obj.values())
        elif isinstance(obj, list):
            return any(check_content(item) for item in obj)
        elif isinstance(obj, str):
            return (
                any(color in obj.lower() for color in ["red", "black"]) or
                any(shape in obj.lower() for shape in ["square", "rectangle"]) or
                any(pos in obj.lower() for pos in ["center", "middle", "position"])
            )
        return False
    
    assert check_content(content), "JSON response should contain image description elements"

@pytest.mark.integration
def test_vision_quality_checks(temp_dir, mock_groq_api_key, sample_image_file):
    """Test basic quality indicators of vision responses"""
    # Test regular response
    result = analyze_image(
        input_file_path=str(sample_image_file),
        prompt="What's in this image?",
        output_directory=str(temp_dir)
    )
    
    # Get content
    output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
    with open(output_file) as f:
        content = f.read()
    
    # Quality checks
    # 1. Response should be substantial (not too short)
    assert len(content) > 50, "Response seems too short"
    
    # 2. Response should be well-formed English
    assert any(word in content.lower() for word in ["the", "is", "are", "in", "on"]), "Response may not be well-formed English"
    
    # 3. Response should contain visual descriptors
    visual_terms = ["color", "shape", "size", "position", "background", "appears", "looks"]
    assert any(term in content.lower() for term in visual_terms), "Response lacks visual descriptors"
    
    # Test JSON response quality
    result_json = analyze_image_json(
        input_file_path=str(sample_image_file),
        prompt="Extract key information from this image as JSON",
        output_directory=str(temp_dir)
    )
    
    # Get JSON content
    output_file = Path(result_json.text.split("saved as: ")[1].split("\n")[0])
    with open(output_file) as f:
        content = json.load(f)
    
    # Quality checks for JSON
    def check_json_quality(obj, depth=0):
        if depth > 5:  # Prevent infinite recursion
            return True
            
        if isinstance(obj, dict):
            # 1. Keys should be descriptive
            keys = obj.keys()
            assert any(len(key) > 2 for key in keys), "JSON keys are too short/non-descriptive"
            
            # 2. Recurse into values
            return all(check_json_quality(v, depth + 1) for v in obj.values())
            
        elif isinstance(obj, list):
            # 3. Lists shouldn't be empty
            assert len(obj) > 0, "Empty lists in JSON response"
            return all(check_json_quality(item, depth + 1) for item in obj)
            
        elif isinstance(obj, str):
            # 4. String values should be meaningful
            return len(obj) > 2
            
        return True
    
    assert check_json_quality(content), "JSON response quality checks failed"

@pytest.mark.integration
def test_vision_robustness(temp_dir, mock_groq_api_key, sample_image_file):
    """Test vision API robustness with different prompts"""
    prompts = [
        "What's in this image?",
        "Describe this image in detail.",
        "List the main elements in this image.",
        "What colors do you see?",
        "Analyze the composition of this image."
    ]
    
    for prompt in prompts:
        result = analyze_image(
            input_file_path=str(sample_image_file),
            prompt=prompt,
            output_directory=str(temp_dir)
        )
        
        # Each prompt should get a meaningful response
        output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
        with open(output_file) as f:
            content = f.read()
            
        # Basic quality checks for each response
        assert len(content) > 50, f"Response too short for prompt: {prompt}"
        assert any(word in content.lower() for word in ["the", "is", "are"]), f"Poor grammar for prompt: {prompt}"
        
        # Response should somewhat match the prompt's focus
        if "color" in prompt.lower():
            assert any(color in content.lower() for color in ["red", "black", "white", "blue", "green"]), "Color prompt got irrelevant response"
        elif "composition" in prompt.lower():
            assert any(term in content.lower() for term in ["position", "layout", "arranged", "placed"]), "Composition prompt got irrelevant response" 