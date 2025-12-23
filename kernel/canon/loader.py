"""
Canon Loader

Loads objectives from trusted sources ONLY.
No runtime injection. No dynamic generation. No external APIs.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import yaml
import hashlib

from .schema import Objective, CanonManifest
from .errors import (
    CanonSchemaViolation,
    CanonError,
)


class CanonLoader:
    """
    Loads objectives from trusted canonical sources.
    
    Trusted sources:
    - YAML files from designated canon directory
    - Signed canon bundles (future)
    
    Explicitly REJECTED:
    - Runtime injection
    - Dynamic generation
    - External API sources
    - Unsigned bundles
    """
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {".yaml", ".yml"}
    
    def __init__(self, canon_path: Path):
        """
        Initialize loader with path to canon directory.
        
        Args:
            canon_path: Path to directory containing canon YAML files
        """
        if not canon_path.exists():
            raise FileNotFoundError(f"Canon path does not exist: {canon_path}")
        if not canon_path.is_dir():
            raise NotADirectoryError(f"Canon path is not a directory: {canon_path}")
        
        self._canon_path = canon_path
        self._loaded_objectives: Dict[str, Objective] = {}
    
    def load_all(self) -> List[Objective]:
        """
        Load all objectives from canon directory.
        
        Returns:
            List of validated Objective instances
            
        Raises:
            CanonSchemaViolation: If any objective fails schema validation
        """
        objectives = []
        
        for file_path in self._canon_path.iterdir():
            if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                continue
            
            if file_path.name.startswith("_"):
                # Skip private/internal files
                continue
            
            loaded = self._load_file(file_path)
            objectives.extend(loaded)
        
        return objectives
    
    def load_file(self, filename: str) -> List[Objective]:
        """
        Load objectives from a specific file.
        
        Args:
            filename: Name of file in canon directory
            
        Returns:
            List of Objective instances from that file
        """
        file_path = self._canon_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Canon file not found: {filename}")
        
        return self._load_file(file_path)
    
    def _load_file(self, file_path: Path) -> List[Objective]:
        """Load objectives from a single YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise CanonSchemaViolation(
                    field="file",
                    message=f"Invalid YAML in {file_path.name}: {e}"
                )
        
        if data is None:
            return []
        
        return self._parse_canon_data(data, file_path.name)
    
    def _parse_canon_data(self, data: Dict[str, Any], source: str) -> List[Objective]:
        """Parse raw YAML data into Objective instances."""
        objectives = []
        
        # Handle direct objective definition
        if "objective" in data:
            obj = self._parse_single_objective(data["objective"], source)
            objectives.append(obj)
        
        # Handle list of objectives
        if "objectives" in data:
            for idx, obj_data in enumerate(data["objectives"]):
                obj = self._parse_single_objective(obj_data, f"{source}[{idx}]")
                objectives.append(obj)
        
        return objectives
    
    def _parse_single_objective(self, data: Dict[str, Any], source: str) -> Objective:
        """Parse a single objective from dict."""
        try:
            # Extract required fields
            obj_id = self._require_field(data, "id", source)
            description = self._require_field(data, "description", source)
            scope = self._require_field(data, "scope", source)
            priority = self._require_field(data, "priority", source)
            
            # Validate scope
            if scope not in ("civilization", "system", "humanity"):
                raise CanonSchemaViolation(
                    field="scope",
                    message=f"Invalid scope '{scope}' in {source}. "
                            f"Must be 'civilization', 'system', or 'humanity'"
                )
            
            # Validate priority
            if not isinstance(priority, int) or priority < 1:
                raise CanonSchemaViolation(
                    field="priority",
                    message=f"Invalid priority '{priority}' in {source}. "
                            f"Must be positive integer"
                )
            
            # Extract optional fields with defaults
            invariants = tuple(data.get("invariants", []))
            termination_conditions = tuple(data.get("termination_conditions", []))
            supersedes = data.get("supersedes")
            
            # Parse created_at if present
            created_at = None
            if "created_at" in data:
                created_at = self._parse_datetime(data["created_at"], source)
            
            return Objective(
                id=obj_id,
                description=description,
                scope=scope,
                priority=priority,
                invariants=invariants,
                termination_conditions=termination_conditions,
                supersedes=supersedes,
                created_at=created_at,
            )
            
        except KeyError as e:
            raise CanonSchemaViolation(
                field=str(e),
                message=f"Missing required field in {source}"
            )
    
    def _require_field(self, data: Dict[str, Any], field: str, source: str) -> Any:
        """Require a field exists and is non-empty."""
        if field not in data:
            raise CanonSchemaViolation(
                field=field,
                message=f"Required field '{field}' missing in {source}"
            )
        
        value = data[field]
        if value is None:
            raise CanonSchemaViolation(
                field=field,
                message=f"Field '{field}' cannot be null in {source}"
            )
        
        return value
    
    def _parse_datetime(self, value: Any, source: str) -> datetime:
        """Parse datetime from various formats."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise CanonSchemaViolation(
                    field="created_at",
                    message=f"Invalid datetime format in {source}: {value}"
                )
        raise CanonSchemaViolation(
            field="created_at",
            message=f"Cannot parse datetime in {source}: {value}"
        )
    
    def compute_canon_hash(self, objectives: List[Objective]) -> str:
        """
        Compute content-addressed hash of entire canon.
        
        This hash is used to verify canon integrity.
        """
        # Sort by ID for deterministic hashing
        sorted_objs = sorted(objectives, key=lambda o: o.id)
        
        hasher = hashlib.sha256()
        for obj in sorted_objs:
            # Hash each objective's content
            content = f"{obj.id}|{obj.description}|{obj.scope}|{obj.priority}"
            content += f"|{'|'.join(obj.invariants)}"
            content += f"|{'|'.join(obj.termination_conditions)}"
            hasher.update(content.encode('utf-8'))
        
        return hasher.hexdigest()
    
    def create_manifest(self, objectives: List[Objective]) -> CanonManifest:
        """Create an immutable manifest of loaded canon."""
        return CanonManifest(
            version="1.0.0",
            objectives=tuple(obj.id for obj in objectives),
            hash=self.compute_canon_hash(objectives),
            sealed_at=datetime.utcnow(),
        )
