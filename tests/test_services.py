import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from unittest.mock import Mock, patch
from backend.services import create_prompts
from flask import Flask

# Mock data
MOCK_USER_DESCRIPTION = "a cat playing with a ball"
MOCK_INITIAL_PROMPTS = [
    '"A cute cat playing with a red ball in a garden"',
    '"A playful cat chasing a ball in the sunlight"',
    '"A cat playing with a ball in a minimalist style"',
    '"A cat and ball in impressionist style"',
    '"A cat playing with a ball in digital art style"',
    '"A cat with a ball in watercolor style"'
]
MOCK_SELECTED_PROMPTS = '"Selected prompt 1: A cute cat playing with a red ball in a garden"\n"Selected prompt 2: A cat playing with a ball in a minimalist style"'
MOCK_EXTRACTED_FEATURES = {
    "0": {
        "style": ["minimalist", "impressionist"],
        "mood": ["playful", "bright"],
        "composition": ["centered", "balanced"]
    }
}

@pytest.fixture
def app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.openai_client = Mock()
    app.style_agent = Mock()
    return app

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client"""
    return Mock()

@pytest.fixture
def mock_style_agent():
    """Create a mock style agent"""
    style_agent = Mock()
    style_agent.extract_features.return_value = MOCK_EXTRACTED_FEATURES
    return style_agent

def test_create_prompts_initial_generation(app, mock_style_agent):
    """Test initial prompt generation without feedback"""
    # Mock the style agent's extract_features method
    app.style_agent.extract_features.return_value = MOCK_EXTRACTED_FEATURES
    
    # Mock the PromptGenerator's generate_prompts method
    with patch('backend.services.PromptGenerator') as mock_generator:
        mock_generator.return_value.generate_prompts.return_value = MOCK_INITIAL_PROMPTS
        
        # Call the function within app context
        with app.app_context():
            result = create_prompts(
                user_description=MOCK_USER_DESCRIPTION,
                is_initial=True
            )
        
        # Verify the result
        assert "prompts" in result
        assert "extracted_features" in result
        assert len(result["prompts"]) == len(MOCK_INITIAL_PROMPTS)
        assert result["extracted_features"] == MOCK_EXTRACTED_FEATURES
        
        # Verify the generator was called with correct parameters
        mock_generator.return_value.generate_prompts.assert_called_once_with(
            user_description=MOCK_USER_DESCRIPTION,
            initial_prompt=True
        )

def test_create_prompts_refined_generation(app, mock_style_agent):
    """Test refined prompt generation with feedback"""
    # Mock the style agent's extract_features method
    app.style_agent.extract_features.return_value = MOCK_EXTRACTED_FEATURES
    
    # Mock the PromptGenerator's generate_prompts method
    with patch('backend.services.PromptGenerator') as mock_generator:
        mock_generator.return_value.generate_prompts.return_value = MOCK_INITIAL_PROMPTS
        
        # Call the function within app context
        with app.app_context():
            result = create_prompts(
                user_description=MOCK_USER_DESCRIPTION,
                selected_prompts=MOCK_SELECTED_PROMPTS,
                is_initial=False
            )
        
        # Verify the result
        assert "prompts" in result
        assert "extracted_features" in result
        assert len(result["prompts"]) == len(MOCK_INITIAL_PROMPTS)
        assert result["extracted_features"] == MOCK_EXTRACTED_FEATURES
        
        # Verify the generator was called with correct parameters
        mock_generator.return_value.generate_prompts.assert_called_once_with(
            user_description=MOCK_USER_DESCRIPTION,
            additional_context=MOCK_SELECTED_PROMPTS
        )

def test_create_prompts_error_handling(app):
    """Test error handling in prompt generation"""
    # Mock the PromptGenerator to raise an exception
    with patch('backend.services.PromptGenerator') as mock_generator:
        mock_generator.return_value.generate_prompts.side_effect = Exception("Test error")
        
        # Test that the function raises an exception within app context
        with app.app_context():
            with pytest.raises(Exception) as exc_info:
                create_prompts(user_description=MOCK_USER_DESCRIPTION)
            
            assert str(exc_info.value) == "Test error"

def test_create_prompts_default_values(app, mock_style_agent):
    """Test prompt generation with default values"""
    # Mock the style agent's extract_features method
    app.style_agent.extract_features.return_value = MOCK_EXTRACTED_FEATURES
    
    # Mock the PromptGenerator's generate_prompts method
    with patch('backend.services.PromptGenerator') as mock_generator:
        mock_generator.return_value.generate_prompts.return_value = MOCK_INITIAL_PROMPTS
        
        # Call the function within app context
        with app.app_context():
            result = create_prompts()
        
        # Verify the result
        assert "prompts" in result
        assert "extracted_features" in result
        assert len(result["prompts"]) == len(MOCK_INITIAL_PROMPTS)
        assert result["extracted_features"] == MOCK_EXTRACTED_FEATURES
        
        # Verify the generator was called with default parameters
        mock_generator.return_value.generate_prompts.assert_called_once_with(
            user_description="Generate a creative and visually appealing image",
            initial_prompt=True
        )