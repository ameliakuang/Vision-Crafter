import json
import torch
import clip
import os
import argparse
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
        For long prompts, splits into chunks and averages their embeddings.
        
        Args:
            prompts: List of prompt strings
            
        Returns:
            Tensor of CLIP embeddings
        """
        with torch.no_grad():
            all_embeddings = []
            
            for prompt in prompts:
                # Split prompt into chunks of roughly 50 tokens (to be safe)
                words = prompt.split()
                chunks = []
                current_chunk = []
                current_length = 0
                
                for word in words:
                    # Rough estimate: each word is about 1.3 tokens
                    word_length = len(word.split()) * 1.3
                    if current_length + word_length > 50:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = [word]
                        current_length = word_length
                    else:
                        current_chunk.append(word)
                        current_length += word_length
                
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                
                # Encode each chunk
                chunk_embeddings = []
                for chunk in chunks:
                    text_tokens = clip.tokenize([chunk]).to(self.device)
                    chunk_embedding = self.model.encode_text(text_tokens)
                    chunk_embeddings.append(chunk_embedding)
                
                # Average the chunk embeddings
                if chunk_embeddings:
                    avg_embedding = torch.mean(torch.stack(chunk_embeddings), dim=0)
                    avg_embedding /= avg_embedding.norm(dim=-1, keepdim=True)
                    all_embeddings.append(avg_embedding.squeeze())  # Remove extra dimension
            
            # Stack all prompt embeddings
            if all_embeddings:
                return torch.stack(all_embeddings)  # Shape: [num_prompts, embedding_dim]
            return torch.tensor([]).to(self.device)

    def calculate_pairwise_similarities(self, embeddings: torch.Tensor) -> np.ndarray:
        """
        Calculate pairwise cosine similarities between embeddings.
        
        Args:
            embeddings: Tensor of CLIP embeddings of shape [num_prompts, embedding_dim]
            
        Returns:
            Matrix of pairwise similarities
        """
        # Ensure embeddings are 2D
        if embeddings.dim() == 1:
            embeddings = embeddings.unsqueeze(0)
        
        # Calculate similarity matrix
        similarity_matrix = torch.matmul(embeddings, embeddings.mT).cpu().numpy()  # Use mT instead of T
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
        print(f"Prompts for round {round_data['round']}: {prompts}")
        
        # Encode prompts
        embeddings = self.encode_prompts(prompts)
        
        # Calculate similarities
        similarity_matrix = self.calculate_pairwise_similarities(embeddings)
        
        # Calculate diversity score
        diversity_score = self.calculate_diversity_score(similarity_matrix)
        
        return diversity_score
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze prompt diversity between rounds')
    parser.add_argument('--base-path', type=str, default='outputs/vision_crafter_20250603_141729',
                      help='Base path containing round data')
    parser.add_argument('--round1', type=int, default=2,
                      help='First round number to compare')
    parser.add_argument('--round2', type=int, default=5, 
                      help='Second round number to compare')
    args = parser.parse_args()

    # Initialize analyzer
    analyzer = PromptDiversityAnalyzer()
    
    # Load round data
    base_path = Path(args.base_path)
    round1_path = os.path.join(base_path, f"round_{args.round1}", "round_data.json")
    round2_path = os.path.join(base_path, f"round_{args.round2}", "round_data.json")
    
    # Load and analyze round 2
    with open(round1_path, 'r') as f:
        round1_data = json.load(f)
    round1_score = analyzer.analyze_round(round1_data)
    
    # Load and analyze round 5
    with open(round2_path, 'r') as f:
        round2_data = json.load(f)
    round2_score = analyzer.analyze_round(round2_data)
    
    # Print results
    print("\nPrompt Diversity Analysis Results:")
    print(f"Round {args.round1} Diversity Score: {round1_score:.4f}")
    print(f"Round {args.round2} Diversity Score: {round2_score:.4f}")
    print(f"Difference (Round {args.round2} - Round {args.round1}): {round2_score - round1_score:.4f}")

if __name__ == "__main__":
    main()
