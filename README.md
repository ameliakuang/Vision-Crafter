# Vision Crafter

An interactive AI-powered image generation application that creates personalized images through iterative feedback and style learning. Vision Crafter combines the power of OpenAI's GPT models for intelligent prompt generation with Together AI's FLUX model for high-quality image generation.

## 🎯 Purpose

Vision Crafter is designed to bridge the gap between human creativity and AI image generation by providing an interactive, feedback-driven experience. Unlike traditional image generators that produce static results, Vision Crafter learns from user preferences and iteratively refines its output to better match user expectations.

## ✨ Key Features

### 🤖 Intelligent Prompt Generation
- **Multi-Style Generation**: Creates diverse prompts with different artistic styles (impressionist, minimalist, digital art, etc.)
- **Context-Aware**: Incorporates user feedback to refine subsequent generations
- **Feature Extraction**: Automatically identifies and highlights key elements in prompts (style, subject, colors, mood, etc.)

### 🎨 Interactive Image Generation
- **Batch Generation**: Produces 6 unique images per generation round
- **Real-time Feedback**: Users can select preferred images and style keywords
- **Iterative Refinement**: Each new generation builds upon previous user preferences
- **Parallel Processing**: Efficiently generates multiple images simultaneously

### 🎯 Smart Learning System
- **Style Preference Learning**: Tracks and incorporates user's preferred artistic styles
- **Prompt History**: Maintains context across generation rounds
- **Feature Highlighting**: Interactive prompt analysis with clickable style elements
- **Session Management**: Organizes generations into rounds with complete metadata

## 🏗️ Architecture

### Backend (Flask + Python)
- **Flask API**: RESTful endpoints for image generation and feedback processing
- **OpenAI Integration**: GPT-4 for intelligent prompt generation and feature extraction
- **Together AI Integration**: FLUX.1-schnell model for high-quality image generation
- **Pipeline Architecture**: Modular design with separate components for prompt generation, style extraction, and image generation
- **Async Processing**: Non-blocking image generation with rate limiting and retry mechanisms

### Frontend (React)
- **Interactive UI**: Modern React interface with real-time feedback
- **Feature Highlighting**: Visual prompt analysis with clickable style elements
- **Image Selection**: Easy selection of preferred images for feedback
- **Responsive Design**: Clean, intuitive user experience

### Core Components
- **PromptGenerator**: Creates diverse, context-aware image prompts
- **StyleExtractionAgent**: Analyzes prompts and extracts visual features
- **PromptGenerationPipeline**: Orchestrates the entire generation process
- **Image Generation Service**: Handles parallel image generation with error handling

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js and npm
- Conda (for environment management)
- API Keys:
  - OpenAI API Key
  - Together AI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vision-crafter
   ```

2. **Set up environment variables**
   Create a `.env` file in the `backend/` directory:
   ```bash
   cd backend
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "TOGETHER_API_KEY=your_together_api_key_here" >> .env
   ```

3. **Create conda environment**
   ```bash
   conda env create -f env.yml
   conda activate vc
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the Flask backend server**
   ```bash
   # From the project root
   python -m backend.run
   ```
   The backend will run on `http://localhost:8000`

2. **Start the React frontend**
   ```bash
   # In a new terminal, from the frontend directory
   cd frontend
   npm start
   ```
   The frontend will open at `http://localhost:3000`

## 📖 Usage Guide

1. **Initial Generation**: Enter a description of the image you want to create
2. **Review Results**: Examine the 6 generated images and their prompts
3. **Provide Feedback**: 
   - Click on images you like to select them
   - Click on highlighted style keywords in prompts to select preferred styles
4. **Iterate**: Click "Generate Images" again to create new images based on your feedback
5. **Explore**: Continue refining through multiple rounds to achieve your desired result





