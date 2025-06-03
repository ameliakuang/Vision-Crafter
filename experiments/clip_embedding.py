import json
import torch
import clip
import os
from pathlib import Path
import numpy as np
from typing import List, Dict
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptDiversityAnalyzer:
    def __init__(self, model_name: str = "ViT-B/32"):
        """
        Initialize the analyzer with CLIP model.
        
        Args:
            model_name: Name of the CLIP model to use
        """
        logger.info(f"Loading CLIP model: {model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        logger.info(f"CLIP model loaded successfully on {self.device}")

    def encode_prompts(self, prompts: List[str]) -> torch.Tensor:
        """
        Encode a list of prompts using CLIP text encoder.
        
        Args:
            prompts: List of prompt strings
            
        Returns:
            Tensor of CLIP embeddings
        """
        with torch.no_grad():
            text_tokens = clip.tokenize(prompts).to(self.device)
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features

    def calculate_pairwise_similarities(self, embeddings: torch.Tensor) -> np.ndarray:
        """
        Calculate pairwise cosine similarities between embeddings.
        
        Args:
            embeddings: Tensor of CLIP embeddings
            
        Returns:
            Matrix of pairwise similarities
        """
        similarity_matrix = torch.matmul(embeddings, embeddings.T).cpu().numpy()
        return similarity_matrix

    def calculate_diversity_score(self, similarity_matrix: np.ndarray) -> float:
        """
        Calculate average pairwise similarity (diversity score).
        
        Args:
            similarity_matrix: Matrix of pairwise similarities
            
        Returns:
            Average pairwise similarity
        """
        # Get upper triangle without diagonal
        upper_triangle = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
        return float(np.mean(upper_triangle))

    def analyze_round(self, round_data: Dict) -> float:
        """
        Analyze a single round's prompts and calculate diversity score.
        
        Args:
            round_data: Dictionary containing round data with prompts
            
        Returns:
            Diversity score for the round
        """
        prompts = [gen["prompt"] for gen in round_data["generations"]]
        logger.info(f"Analyzing {len(prompts)} prompts from round {round_data['round']}")
        
        # Encode prompts
        embeddings = self.encode_prompts(prompts)
        
        # Calculate similarities
        similarity_matrix = self.calculate_pairwise_similarities(embeddings)
        
        # Calculate diversity score
        diversity_score = self.calculate_diversity_score(similarity_matrix)
        
        return diversity_score

def main():
    # Initialize analyzer
    analyzer = PromptDiversityAnalyzer()
    
    # Load round data
    base_path = Path("outputs/vision_crafter_20250603_141729")
    round2_path = os.path.join(base_path, "round_2", "round_data.json")
    round5_path = os.path.join(base_path, "round_5", "round_data.json")
    
    # Load and analyze round 2
    with open(round2_path, 'r') as f:
        round2_data = json.load(f)
    round2_score = analyzer.analyze_round(round2_data)
    
    # Load and analyze round 5
    with open(round5_path, 'r') as f:
        round5_data = json.load(f)
    round5_score = analyzer.analyze_round(round5_data)
    
    # Print results
    print("\nPrompt Diversity Analysis Results:")
    print(f"Round 2 Diversity Score: {round2_score:.4f}")
    print(f"Round 5 Diversity Score: {round5_score:.4f}")
    print(f"Difference (Round 5 - Round 2): {round5_score - round2_score:.4f}")

if __name__ == "__main__":
    main()
