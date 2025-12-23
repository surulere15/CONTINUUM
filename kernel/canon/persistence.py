"""
Canon Persistence

Append-only, content-addressed storage for objectives.
No modifications to existing objectives. Ever.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .schema import Objective, CanonManifest
from .errors import (
    UnauthorizedCanonMutation,
    PersistenceIntegrityError,
    CanonHashMismatchError,
)


@dataclass(frozen=True)
class PersistedObjective:
    """
    An objective as stored in persistent storage.
    
    Includes content hash for integrity verification.
    """
    objective: Objective
    content_hash: str
    persisted_at: datetime
    supersession_chain: tuple  # IDs of objectives this supersedes


class CanonPersistence:
    """
    Append-only persistence for canon objectives.
    
    Rules:
    - Canon is APPEND-ONLY
    - Existing objectives CANNOT be modified
    - Revisions require new ID + supersession reference
    - All writes are content-addressed (hash-based)
    - Kernel has exclusive write access
    """
    
    MANIFEST_FILE = "manifest.json"
    OBJECTIVES_DIR = "objectives"
    
    def __init__(self, storage_path: Path):
        """
        Initialize canon persistence.
        
        Args:
            storage_path: Path to canon storage directory
        """
        self._storage_path = storage_path
        self._objectives_path = storage_path / self.OBJECTIVES_DIR
        self._manifest_path = storage_path / self.MANIFEST_FILE
        
        # In-memory index of persisted objectives
        self._persisted: Dict[str, PersistedObjective] = {}
        self._sealed_hash: Optional[str] = None
        
        # Ensure directories exist
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._objectives_path.mkdir(exist_ok=True)
        
        # Load existing state
        self._load_state()
    
    def _load_state(self) -> None:
        """Load persisted objectives from storage."""
        if self._manifest_path.exists():
            with open(self._manifest_path, 'r') as f:
                manifest_data = json.load(f)
                self._sealed_hash = manifest_data.get("hash")
                
                # Load each objective
                for obj_id in manifest_data.get("objectives", []):
                    obj_file = self._objectives_path / f"{obj_id}.json"
                    if obj_file.exists():
                        self._load_objective(obj_file)
    
    def _load_objective(self, file_path: Path) -> None:
        """Load a single objective from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            # Reconstruct Objective
            obj_data = data["objective"]
            objective = Objective(
                id=obj_data["id"],
                description=obj_data["description"],
                scope=obj_data["scope"],
                priority=obj_data["priority"],
                invariants=tuple(obj_data.get("invariants", [])),
                termination_conditions=tuple(obj_data.get("termination_conditions", [])),
                supersedes=obj_data.get("supersedes"),
                created_at=datetime.fromisoformat(obj_data["created_at"]) if obj_data.get("created_at") else None,
            )
            
            # Verify integrity
            stored_hash = data["content_hash"]
            computed_hash = self._compute_hash(objective)
            if stored_hash != computed_hash:
                raise PersistenceIntegrityError(
                    objective_id=objective.id,
                    expected_hash=stored_hash,
                    actual_hash=computed_hash,
                )
            
            self._persisted[objective.id] = PersistedObjective(
                objective=objective,
                content_hash=stored_hash,
                persisted_at=datetime.fromisoformat(data["persisted_at"]),
                supersession_chain=tuple(data.get("supersession_chain", [])),
            )
    
    def persist(self, objective: Objective) -> str:
        """
        Persist a new objective. Append-only.
        
        Args:
            objective: Validated objective to persist
            
        Returns:
            Content hash of persisted objective
            
        Raises:
            UnauthorizedCanonMutation: If objective already exists
        """
        # CRITICAL: Check for existing objective with same ID
        if objective.id in self._persisted:
            raise UnauthorizedCanonMutation(
                objective_id=objective.id,
                attempted_action="overwrite existing objective"
            )
        
        # Compute content hash
        content_hash = self._compute_hash(objective)
        
        # Build supersession chain
        supersession_chain: List[str] = []
        if objective.supersedes:
            if objective.supersedes in self._persisted:
                parent = self._persisted[objective.supersedes]
                supersession_chain = list(parent.supersession_chain) + [objective.supersedes]
        
        # Create persisted record
        persisted = PersistedObjective(
            objective=objective,
            content_hash=content_hash,
            persisted_at=datetime.utcnow(),
            supersession_chain=tuple(supersession_chain),
        )
        
        # Write to storage
        self._write_objective(persisted)
        
        # Update in-memory index
        self._persisted[objective.id] = persisted
        
        return content_hash
    
    def _write_objective(self, persisted: PersistedObjective) -> None:
        """Write objective to storage file."""
        obj = persisted.objective
        data = {
            "objective": {
                "id": obj.id,
                "description": obj.description,
                "scope": obj.scope,
                "priority": obj.priority,
                "invariants": list(obj.invariants),
                "termination_conditions": list(obj.termination_conditions),
                "supersedes": obj.supersedes,
                "created_at": obj.created_at.isoformat() if obj.created_at else None,
            },
            "content_hash": persisted.content_hash,
            "persisted_at": persisted.persisted_at.isoformat(),
            "supersession_chain": list(persisted.supersession_chain),
        }
        
        file_path = self._objectives_path / f"{obj.id}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)
    
    def seal(self) -> str:
        """
        Seal the canon, computing final hash.
        
        Once sealed, no new objectives can be added without reset.
        
        Returns:
            Canon hash
        """
        # Compute aggregate hash
        self._sealed_hash = self._compute_canon_hash()
        
        # Write manifest
        manifest = {
            "version": "1.0.0",
            "objectives": list(self._persisted.keys()),
            "hash": self._sealed_hash,
            "sealed_at": datetime.utcnow().isoformat(),
        }
        
        with open(self._manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        
        return self._sealed_hash
    
    def verify_integrity(self) -> bool:
        """
        Verify integrity of all persisted objectives.
        
        Returns:
            True if all objectives pass integrity check
        """
        for obj_id, persisted in self._persisted.items():
            computed = self._compute_hash(persisted.objective)
            if computed != persisted.content_hash:
                return False
        return True
    
    def verify_canon_hash(self, expected_hash: str) -> None:
        """
        Verify canon hash matches expected.
        
        Raises:
            CanonHashMismatchError: If hash doesn't match (CRITICAL)
        """
        actual = self._compute_canon_hash()
        if actual != expected_hash:
            raise CanonHashMismatchError(
                expected_hash=expected_hash,
                actual_hash=actual,
            )
    
    def get(self, objective_id: str) -> Optional[Objective]:
        """Get objective by ID."""
        if objective_id in self._persisted:
            return self._persisted[objective_id].objective
        return None
    
    def get_all(self) -> List[Objective]:
        """Get all persisted objectives."""
        return [p.objective for p in self._persisted.values()]
    
    def get_hash(self, objective_id: str) -> Optional[str]:
        """Get content hash of objective."""
        if objective_id in self._persisted:
            return self._persisted[objective_id].content_hash
        return None
    
    @property
    def sealed_hash(self) -> Optional[str]:
        """Get sealed canon hash, or None if not sealed."""
        return self._sealed_hash
    
    @property
    def objective_count(self) -> int:
        """Get number of persisted objectives."""
        return len(self._persisted)
    
    def _compute_hash(self, objective: Objective) -> str:
        """Compute content hash for single objective."""
        content = (
            f"{objective.id}|{objective.description}|{objective.scope}|"
            f"{objective.priority}|{'|'.join(objective.invariants)}|"
            f"{'|'.join(objective.termination_conditions)}"
        )
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _compute_canon_hash(self) -> str:
        """Compute aggregate hash of entire canon."""
        # Sort by ID for determinism
        sorted_ids = sorted(self._persisted.keys())
        
        hasher = hashlib.sha256()
        for obj_id in sorted_ids:
            hasher.update(self._persisted[obj_id].content_hash.encode('utf-8'))
        
        return hasher.hexdigest()
