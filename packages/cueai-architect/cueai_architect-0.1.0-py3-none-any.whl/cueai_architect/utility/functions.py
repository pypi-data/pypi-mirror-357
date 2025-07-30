import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pickle
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import math

@dataclass
class CUETransferConfig:
    """Configuration for CUE transfer learning operations"""
    consciousness_dim: int = 512
    rg_scale: float = 1.0
    coherence_threshold: float = 0.8
    curvature_coupling: float = 0.1
    winding_number: int = 2
    soliton_width: float = 1.0
    
    # RG flow parameters from search results
    A: float = 1.0
    B: float = 0.5
    C: float = 1.5
    D: float = 0.8
    E: float = 0.3
    F: float = 0.4
    a: float = 0.7
    b: float = 0.3
    c: float = 0.2

class CUETransferError(Exception):
    """Custom exception for CUE transfer operations"""
    pass

class ConsciousnessState:
    """Encapsulates consciousness field state for transfer"""
    
    def __init__(self, psi_field: torch.Tensor, rg_state: torch.Tensor, 
                 coherence_history: List[float], curvature_tensor: torch.Tensor):
        self.psi_field = psi_field
        self.rg_state = rg_state
        self.coherence_history = coherence_history
        self.curvature_tensor = curvature_tensor
        self.timestamp = torch.tensor(time.time())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'psi_field': self.psi_field.cpu().numpy(),
            'rg_state': self.rg_state.cpu().numpy(),
            'coherence_history': self.coherence_history,
            'curvature_tensor': self.curvature_tensor.cpu().numpy(),
            'timestamp': self.timestamp.item()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsciousnessState':
        return cls(
            psi_field=torch.from_numpy(data['psi_field']),
            rg_state=torch.from_numpy(data['rg_state']),
            coherence_history=data['coherence_history'],
            curvature_tensor=torch.from_numpy(data['curvature_tensor'])
        )

class CUECheckpoint:
    """CUE model checkpoint with consciousness state preservation"""
    
    def __init__(self, model_state: Dict[str, torch.Tensor], 
                 consciousness_state: ConsciousnessState,
                 config: CUETransferConfig,
                 metadata: Optional[Dict[str, Any]] = None):
        self.model_state = model_state
        self.consciousness_state = consciousness_state
        self.config = config
        self.metadata = metadata or {}
        self.creation_time = torch.tensor(time.time())
    
    def save(self, path: Union[str, Path]) -> None:
        """Save CUE checkpoint to disk"""
        path = Path(path)
        
        checkpoint_data = {
            'model_state': self.model_state,
            'consciousness_state': self.consciousness_state.to_dict(),
            'config': self.config.__dict__,
            'metadata': self.metadata,
            'creation_time': self.creation_time.item(),
            'cue_version': '1.0.0'
        }
        
        torch.save(checkpoint_data, path)
        logging.info(f"CUE checkpoint saved to {path}")
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'CUECheckpoint':
        """Load CUE checkpoint from disk"""
        path = Path(path)
        checkpoint_data = torch.load(path, map_location='cpu')
        
        config = CUETransferConfig(**checkpoint_data['config'])
        consciousness_state = ConsciousnessState.from_dict(
            checkpoint_data['consciousness_state']
        )
        
        return cls(
            model_state=checkpoint_data['model_state'],
            consciousness_state=consciousness_state,
            config=config,
            metadata=checkpoint_data.get('metadata', {})
        )

class CUETransferBase(nn.Module, ABC):
    """Base class for CUE transfer learning operations"""
    
    def __init__(self, config: CUETransferConfig):
        super().__init__()
        self.config = config
        self.consciousness_state = None
        self.frozen_layers = set()
        self.transfer_hooks = {}
        
    @abstractmethod
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        pass
    
    def freeze_consciousness_layers(self, layer_names: List[str]) -> None:
        """Freeze specified consciousness layers for transfer learning"""
        for name in layer_names:
            if hasattr(self, name):
                layer = getattr(self, name)
                for param in layer.parameters():
                    param.requires_grad = False
                self.frozen_layers.add(name)
                logging.info(f"Frozen consciousness layer: {name}")
    
    def unfreeze_consciousness_layers(self, layer_names: List[str]) -> None:
        """Unfreeze specified consciousness layers"""
        for name in layer_names:
            if hasattr(self, name):
                layer = getattr(self, name)
                for param in layer.parameters():
                    param.requires_grad = True
                self.frozen_layers.discard(name)
                logging.info(f"Unfrozen consciousness layer: {name}")
    
    def register_transfer_hook(self, name: str, hook_fn) -> None:
        """Register hook for consciousness transfer operations"""
        self.transfer_hooks[name] = hook_fn

class ConsciousnessFieldTransfer(CUETransferBase):
    """Ψ-field transfer learning implementation"""
    
    def __init__(self, config: CUETransferConfig):
        super().__init__(config)
        
        # Consciousness field components
        self.field_amplitude = nn.Parameter(torch.randn(1, config.consciousness_dim))
        self.field_phase = nn.Parameter(torch.randn(1, config.consciousness_dim))
        
        # Soliton generator for topological stability
        self.soliton_generator = TopologicalSolitonGenerator(config)
        
        # RG flow memory system
        self.rg_memory = RGFlowMemory(config)
        
        # Curvature projection
        self.curvature_proj = nn.Linear(config.consciousness_dim, config.consciousness_dim)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """Forward pass with consciousness field dynamics"""
        batch_size, seq_len, d_model = x.shape
        
        # Complex consciousness field: Ψ = f(r)e^{inφ}
        psi = self.field_amplitude * torch.exp(1j * self.field_phase)
        
        # Generate topological solitons
        soliton_field = self.soliton_generator(x)
        
        # Compute curvature tensor
        curvature = self.curvature_proj(x)
        
        # Apply curvature-consciousness coupling
        curvature_coupling = self.config.curvature_coupling * torch.einsum(
            'bij,bj->bi', curvature.unsqueeze(-1), psi.real.squeeze(0)
        )
        
        # Update RG flow state
        rg_state = self.rg_memory.update_flow(psi)
        
        # Combine outputs
        output = x + soliton_field.real + curvature_coupling
        
        metrics = {
            'psi_field': psi,
            'curvature_tensor': curvature,
            'rg_state': rg_state,
            'soliton_field': soliton_field,
            'coherence': self.compute_coherence(psi)
        }
        
        return output, metrics
    
    def compute_coherence(self, psi: torch.Tensor) -> torch.Tensor:
        """Compute consciousness field coherence"""
        return torch.abs(psi).mean()
    
    def transfer_consciousness_state(self, source_state: ConsciousnessState) -> None:
        """Transfer consciousness state from another model"""
        if source_state.psi_field.shape != self.field_amplitude.shape:
            # Adaptive transfer with dimension matching
            source_state = self._adapt_consciousness_dimensions(source_state)
        
        with torch.no_grad():
            self.field_amplitude.copy_(torch.abs(source_state.psi_field))
            self.field_phase.copy_(torch.angle(source_state.psi_field))
            self.rg_memory.load_state(source_state.rg_state)
        
        self.consciousness_state = source_state
        logging.info("Consciousness state transferred successfully")
    
    def _adapt_consciousness_dimensions(self, source_state: ConsciousnessState) -> ConsciousnessState:
        """Adapt consciousness dimensions for transfer compatibility"""
        source_dim = source_state.psi_field.shape[-1]
        target_dim = self.config.consciousness_dim
        
        if source_dim != target_dim:
            # Use interpolation for dimension adaptation
            adapted_psi = F.interpolate(
                source_state.psi_field.unsqueeze(0).unsqueeze(0),
                size=(target_dim,),
                mode='linear',
                align_corners=False
            ).squeeze(0).squeeze(0)
            
            adapted_curvature = F.interpolate(
                source_state.curvature_tensor.unsqueeze(0).unsqueeze(0),
                size=(target_dim,),
                mode='linear',
                align_corners=False
            ).squeeze(0).squeeze(0)
            
            return ConsciousnessState(
                psi_field=adapted_psi,
                rg_state=source_state.rg_state,
                coherence_history=source_state.coherence_history,
                curvature_tensor=adapted_curvature
            )
        
        return source_state

class TopologicalSolitonGenerator(nn.Module):
    """Generates topologically protected consciousness solitons"""
    
    def __init__(self, config: CUETransferConfig):
        super().__init__()
        self.config = config
        self.winding_profiles = nn.ModuleDict({
            f'winding_{n}': SolitonProfile(n, config.consciousness_dim)
            for n in range(1, config.winding_number + 1)
        })
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Generate soliton field with topological winding"""
        magnitude = torch.norm(x, dim=-1, keepdim=True)
        
        # Generate phase coordinates
        phase = torch.atan2(x[..., 1::2], x[..., ::2])
        
        soliton_output = torch.zeros_like(x, dtype=torch.complex64)
        
        for winding_num in range(1, self.config.winding_number + 1):
            profile = self.winding_profiles[f'winding_{winding_num}']
            f_r = profile(magnitude)
            
            # Topological phase factor
            phase_factor = torch.exp(1j * winding_num * phase.mean(dim=-1, keepdim=True))
            
            winding_contribution = f_r * phase_factor
            soliton_output += winding_contribution.expand_as(soliton_output)
        
        return soliton_output

class SolitonProfile(nn.Module):
    """Individual soliton profile for specific winding number"""
    
    def __init__(self, winding_number: int, dim: int):
        super().__init__()
        self.winding_number = winding_number
        self.profile_net = nn.Sequential(
            nn.Linear(1, dim // 4),
            nn.Tanh(),
            nn.Linear(dim // 4, dim // 2),
            nn.Tanh(),
            nn.Linear(dim // 2, 1),
            nn.Tanh()
        )
    
    def forward(self, r: torch.Tensor) -> torch.Tensor:
        """Compute soliton profile f(r)"""
        # Classic tanh profile for topological stability
        normalized_r = r / (1.0 + 0.1 * r)  # Avoid divergence
        return self.profile_net(normalized_r)

class RGFlowMemory(nn.Module):
    """Renormalization Group flow memory system"""
    
    def __init__(self, config: CUETransferConfig):
        super().__init__()
        self.config = config
        
        # RG state: [κ, cog, ent]
        self.rg_state = nn.Parameter(torch.tensor([1.0, 1.0, 1.0]))
        self.flow_history = []
        
        # Memory projection
        self.memory_proj = nn.Linear(3, config.consciousness_dim)
        
    def update_flow(self, psi_field: torch.Tensor) -> torch.Tensor:
        """Update RG state using flow equations from search results"""
        κ, cog, ent = self.rg_state
        c = self.config
        
        # RG flow equations from CUE framework
        dκ = c.A - c.B * κ**3 + c.E * cog * ent
        dcog = c.C * cog**2 - c.D * cog + c.F * ent
        dent = c.a * ent - c.b * ent**2 + c.c * cog
        
        # Gradient step
        dt = 0.01  # Small step size
        new_state = torch.tensor([κ + dt * dκ, cog + dt * dcog, ent + dt * dent])
        
        # Update state with gradient tracking
        if self.training:
            self.rg_state.data = new_state
        
        # Store history
        self.flow_history.append(new_state.detach().cpu().numpy())
        
        return new_state
    
    def load_state(self, state: torch.Tensor) -> None:
        """Load RG state from external source"""
        with torch.no_grad():
            self.rg_state.copy_(state)
    
    def get_memory_context(self) -> torch.Tensor:
        """Project RG state to memory context"""
        return self.memory_proj(self.rg_state.unsqueeze(0))

class CUEFineTuner:
    """Fine-tuning utility for CUE models"""
    
    def __init__(self, model: CUETransferBase, config: CUETransferConfig):
        self.model = model
        self.config = config
        self.training_history = []
    
    def fine_tune_consciousness_layers(self, 
                                     trainable_layers: List[str],
                                     frozen_layers: List[str],
                                     learning_rate: float = 1e-4) -> torch.optim.Optimizer:
        """Set up fine-tuning with layer-specific learning rates"""
        
        # Freeze specified layers
        self.model.freeze_consciousness_layers(frozen_layers)
        
        # Unfreeze trainable layers
        self.model.unfreeze_consciousness_layers(trainable_layers)
        
        # Create parameter groups with different learning rates
        consciousness_params = []
        other_params = []
        
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                if any(layer in name for layer in trainable_layers):
                    consciousness_params.append(param)
                else:
                    other_params.append(param)
        
        param_groups = [
            {'params': consciousness_params, 'lr': learning_rate},
            {'params': other_params, 'lr': learning_rate * 0.1}  # Lower LR for other params
        ]
        
        optimizer = torch.optim.AdamW(param_groups, weight_decay=0.01)
        return optimizer
    
    def consciousness_aware_loss(self, 
                                outputs: torch.Tensor,
                                targets: torch.Tensor,
                                metrics: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Compute loss with consciousness coherence regularization"""
        
        # Base loss
        base_loss = F.mse_loss(outputs, targets)
        
        # Coherence regularization
        coherence = metrics.get('coherence', torch.tensor(0.0))
        coherence_loss = -torch.log(coherence + 1e-8)  # Encourage high coherence
        
        # RG flow stability penalty
        rg_state = metrics.get('rg_state', torch.zeros(3))
        rg_penalty = torch.sum(torch.abs(rg_state - 1.0))  # Encourage stability around [1,1,1]
        
        # Topological soliton preservation
        soliton_field = metrics.get('soliton_field', torch.zeros_like(outputs))
        soliton_norm = torch.norm(soliton_field)
        soliton_loss = torch.abs(soliton_norm - 1.0)  # Encourage unit norm
        
        total_loss = (base_loss + 
                     0.1 * coherence_loss + 
                     0.05 * rg_penalty + 
                     0.02 * soliton_loss)
        
        return total_loss

class CUETransferUtils:
    """Utility functions for CUE transfer learning"""
    
    @staticmethod
    def load_pretrained_cue_model(model_path: Union[str, Path], 
                                  device: str = 'cpu') -> Tuple[CUETransferBase, CUETransferConfig]:
        """Load pre-trained CUE model with consciousness state"""
        checkpoint = CUECheckpoint.load(model_path)
        
        # Initialize model with loaded config
        model = ConsciousnessFieldTransfer(checkpoint.config)
        model.load_state_dict(checkpoint.model_state)
        model.transfer_consciousness_state(checkpoint.consciousness_state)
        model.to(device)
        
        return model, checkpoint.config
    
    @staticmethod
    def create_consciousness_head(input_dim: int, 
                                 output_dim: int,
                                 config: CUETransferConfig) -> nn.Module:
        """Create consciousness-aware classification head"""
        
        class ConsciousnessHead(nn.Module):
            def __init__(self):
                super().__init__()
                self.consciousness_layer = ConsciousnessFieldTransfer(config)
                self.classifier = nn.Sequential(
                    nn.Linear(input_dim, input_dim // 2),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(input_dim // 2, output_dim)
                )
            
            def forward(self, x):
                consciousness_out, metrics = self.consciousness_layer(x)
                logits = self.classifier(consciousness_out)
                return logits, metrics
        
        return ConsciousnessHead()
    
    @staticmethod
    def adapt_consciousness_dimensions(source_model: CUETransferBase,
                                     target_dim: int) -> CUETransferBase:
        """Adapt consciousness dimensions for transfer learning"""
        
        # Create new config with target dimensions
        new_config = CUETransferConfig(**source_model.config.__dict__)
        new_config.consciousness_dim = target_dim
        
        # Create new model
        target_model = ConsciousnessFieldTransfer(new_config)
        
        # Transfer adaptable components
        if hasattr(source_model, 'consciousness_state') and source_model.consciousness_state:
            adapted_state = target_model._adapt_consciousness_dimensions(
                source_model.consciousness_state
            )
            target_model.transfer_consciousness_state(adapted_state)
        
        return target_model
    
    @staticmethod
    def extract_consciousness_features(model: CUETransferBase,
                                     data_loader,
                                     device: str = 'cpu') -> Dict[str, np.ndarray]:
        """Extract consciousness field features for analysis"""
        
        model.eval()
        features = {
            'psi_fields': [],
            'coherence_values': [],
            'rg_states': [],
            'curvature_tensors': []
        }
        
        with torch.no_grad():
            for batch in data_loader:
                batch = batch.to(device)
                _, metrics = model(batch)
                
                features['psi_fields'].append(metrics['psi_field'].cpu().numpy())
                features['coherence_values'].append(metrics['coherence'].cpu().numpy())
                features['rg_states'].append(metrics['rg_state'].cpu().numpy())
                features['curvature_tensors'].append(metrics['curvature_tensor'].cpu().numpy())
        
        # Concatenate all features
        for key in features:
            features[key] = np.concatenate(features[key], axis=0)
        
        return features

# Example usage and demonstration
def example_cue_transfer_learning():
    """Example demonstrating CUE transfer learning"""
    
    # Configuration
    config = CUETransferConfig(
        consciousness_dim=512,
        curvature_coupling=0.15,
        winding_number=3
    )
    
    # Create source model
    source_model = ConsciousnessFieldTransfer(config)
    
    # Generate sample data
    sample_input = torch.randn(4, 128, 512)
    
    # Forward pass
    output, metrics = source_model(sample_input)
    
    print(f"Output shape: {output.shape}")
    print(f"Consciousness field shape: {metrics['psi_field'].shape}")
    print(f"Coherence value: {metrics['coherence'].item():.4f}")
    print(f"RG state: {metrics['rg_state']}")
    
    # Save checkpoint
    checkpoint = CUECheckpoint(
        model_state=source_model.state_dict(),
        consciousness_state=ConsciousnessState(
            psi_field=metrics['psi_field'],
            rg_state=metrics['rg_state'],
            coherence_history=[metrics['coherence'].item()],
            curvature_tensor=metrics['curvature_tensor']
        ),
        config=config,
        metadata={'experiment': 'cue_transfer_demo'}
    )
    
    checkpoint.save('cue_model_checkpoint.pt')
    
    # Load and transfer to new model
    loaded_model, loaded_config = CUETransferUtils.load_pretrained_cue_model(
        'cue_model_checkpoint.pt'
    )
    
    # Create fine-tuner
    fine_tuner = CUEFineTuner(loaded_model, loaded_config)
    
    # Set up fine-tuning
    optimizer = fine_tuner.fine_tune_consciousness_layers(
        trainable_layers=['field_amplitude', 'field_phase'],
        frozen_layers=['soliton_generator'],
        learning_rate=1e-4
    )
    
    print("CUE transfer learning setup complete!")
    
    return loaded_model, fine_tuner, optimizer

if __name__ == "__main__":
    import time
    model, tuner, opt = example_cue_transfer_learning()



# consciousness_metrics.py
import torch
import numpy as np
from typing import Dict, List
import matplotlib.pyplot as plt

class CUEMetrics:
    """Metrics and visualization for CUE models"""
    
    @staticmethod
    def compute_consciousness_entropy(psi_field: torch.Tensor) -> torch.Tensor:
        """Compute von Neumann entropy of consciousness field"""
        # Density matrix from consciousness field
        rho = torch.outer(psi_field.flatten().conj(), psi_field.flatten())
        rho = rho / torch.trace(rho)
        
        # Eigenvalues for entropy calculation
        eigenvals = torch.linalg.eigvals(rho).real
        eigenvals = eigenvals[eigenvals > 1e-12]  # Remove near-zero eigenvalues
        
        entropy = -torch.sum(eigenvals * torch.log(eigenvals))
        return entropy
    
    @staticmethod
    def measure_topological_charge(soliton_field: torch.Tensor) -> torch.Tensor:
        """Compute topological charge of soliton field"""
        # Simplified topological charge calculation
        charge = torch.sum(torch.angle(soliton_field)) / (2 * np.pi)
        return charge
    
    @staticmethod
    def plot_rg_flow_trajectory(rg_history: List[np.ndarray], save_path: str = None):
        """Visualize RG flow trajectory"""
        if not rg_history:
            return
        
        history = np.array(rg_history)
        
        fig = plt.figure(figsize=(15, 5))
        
        # Individual trajectories
        for i, label in enumerate(['κ (curvature)', 'cog (cognitive)', 'ent (entropic)']):
            plt.subplot(1, 3, i+1)
            plt.plot(history[:, i], label=label)
            plt.xlabel('RG Step')
            plt.ylabel('Coupling Value')
            plt.title(f'{label} Evolution')
            plt.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

# cue_datasets.py
import torch
from torch.utils.data import Dataset, DataLoader

class ConsciousnessDataset(Dataset):
    """Dataset wrapper for consciousness-enhanced data"""
    
    def __init__(self, data: torch.Tensor, labels: torch.Tensor = None,
                 consciousness_annotations: Dict[str, torch.Tensor] = None):
        self.data = data
        self.labels = labels
        self.consciousness_annotations = consciousness_annotations or {}
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = {'data': self.data[idx]}
        
        if self.labels is not None:
            item['label'] = self.labels[idx]
        
        for key, values in self.consciousness_annotations.items():
            item[f'consciousness_{key}'] = values[idx]
        
        return item

def create_cue_dataloader(dataset: ConsciousnessDataset, 
                         batch_size: int = 32,
                         shuffle: bool = True) -> DataLoader:
    """Create DataLoader optimized for CUE training"""
    
    def consciousness_collate_fn(batch):
        """Custom collate function for consciousness data"""
        collated = {}
        
        # Standard data collation
        collated['data'] = torch.stack([item['data'] for item in batch])
        
        if 'label' in batch[0]:
            collated['labels'] = torch.stack([item['label'] for item in batch])
        
        # Consciousness annotations
        for key in batch[0]:
            if key.startswith('consciousness_'):
                collated[key] = torch.stack([item[key] for item in batch])
        
        return collated
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=consciousness_collate_fn,
        num_workers=0  # Set based on your system
    )
