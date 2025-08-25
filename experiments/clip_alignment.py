import torch
import clip
import lpips
from PIL import Image
import torchvision.transforms as transforms
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageSimilarityAnalyzer:
    def __init__(self, clip_model_name: str = "ViT-B/32"):
        """
        Initialize the analyzer with CLIP and LPIPS models.
        
        Args:
            clip_model_name: Name of the CLIP model to use
        """
        logger.info(f"Loading CLIP model: {clip_model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.preprocess = clip.load(clip_model_name, device=self.device)
        
        logger.info("Loading LPIPS model")
        self.lpips_model = lpips.LPIPS(net='alex').to(self.device)
        
        # Define image transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                              std=[0.229, 0.224, 0.225])
        ])
        
        logger.info(f"Models loaded successfully on {self.device}")

    def load_image(self, image_path: str) -> torch.Tensor:
        """
        Load and preprocess an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image tensor
        """
        image = Image.open(image_path).convert('RGB')
        return self.preprocess(image).unsqueeze(0).to(self.device)

    def compute_clip_similarity(self, img1: torch.Tensor, img2: torch.Tensor) -> float:
        """
        Compute CLIP similarity between two images.
        
        Args:
            img1: First image tensor
            img2: Second image tensor
            
        Returns:
            Cosine similarity score
        """
        with torch.no_grad():
            # Get image features
            img1_features = self.clip_model.encode_image(img1)
            img2_features = self.clip_model.encode_image(img2)
            
            # Normalize features
            img1_features /= img1_features.norm(dim=-1, keepdim=True)
            img2_features /= img2_features.norm(dim=-1, keepdim=True)
            
            # Compute similarity
            similarity = torch.matmul(img1_features, img2_features.T).item()
            
        return similarity

    def compute_lpips_similarity(self, img1: torch.Tensor, img2: torch.Tensor) -> float:
        """
        Compute LPIPS similarity between two images.
        
        Args:
            img1: First image tensor
            img2: Second image tensor
            
        Returns:
            LPIPS similarity score (lower is more similar)
        """
        with torch.no_grad():
            # Convert CLIP preprocessed images to the format expected by LPIPS
            # First denormalize the images
            mean = torch.tensor([0.48145466, 0.4578275, 0.40821073]).view(1, 3, 1, 1).to(self.device)
            std = torch.tensor([0.26862954, 0.26130258, 0.27577711]).view(1, 3, 1, 1).to(self.device)
            
            img1_denorm = img1 * std + mean
            img2_denorm = img2 * std + mean
            
            # Clamp values to [0, 1] range
            img1_denorm = torch.clamp(img1_denorm, 0, 1)
            img2_denorm = torch.clamp(img2_denorm, 0, 1)
            
            # Compute LPIPS distance
            similarity = self.lpips_model(img1_denorm, img2_denorm).item()
            
        return similarity

def main():
    # Initialize analyzer
    analyzer = ImageSimilarityAnalyzer()
    
    # Define image paths
    reference_path = "cat_sleeping_under_tree.png"
    round2_path = r"C:\Users\kuang\Repos\vision-crafter\outputs\vision_crafter_20250603_141729\round_2\image_1.png"
    round5_path = r"C:\Users\kuang\Repos\vision-crafter\outputs\vision_crafter_20250603_141729\round_5\image_2.png"
    
    # Load images
    logger.info("Loading images...")
    reference_img = analyzer.load_image(reference_path)
    round2_img = analyzer.load_image(round2_path)
    round5_img = analyzer.load_image(round5_path)
    
    # Compute similarities
    logger.info("Computing similarities...")
    
    # CLIP similarities
    clip_sim_round2 = analyzer.compute_clip_similarity(reference_img, round2_img)
    clip_sim_round5 = analyzer.compute_clip_similarity(reference_img, round5_img)
    
    # LPIPS similarities
    lpips_sim_round2 = analyzer.compute_lpips_similarity(reference_img, round2_img)
    lpips_sim_round5 = analyzer.compute_lpips_similarity(reference_img, round5_img)
    
    # Print results
    print("\nImage Similarity Analysis Results:")
    print("\nCLIP Similarity (higher is more similar):")
    print(f"Round 2: {clip_sim_round2:.4f}")
    print(f"Round 5: {clip_sim_round5:.4f}")
    print(f"Round 2 is {'more' if clip_sim_round2 > clip_sim_round5 else 'less'} similar to reference")
    
    print("\nLPIPS Similarity (lower is more similar):")
    print(f"Round 2: {lpips_sim_round2:.4f}")
    print(f"Round 5: {lpips_sim_round5:.4f}")
    print(f"Round 2 is {'more' if lpips_sim_round2 < lpips_sim_round5 else 'less'} similar to reference")

if __name__ == "__main__":
    main()
