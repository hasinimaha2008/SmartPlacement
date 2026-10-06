import re
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.models import Skill
from app.schemas.schemas import ExtractedSkill, SkillExtractionResponse

class SkillService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_canonical_skill_registry(self) -> Dict[str, Dict]:
        """
        Builds in-memory lookup table of canonical skills and aliases.
        """
        registry = {}
        if self.db:
            skills = self.db.query(Skill).all()
            for s in skills:
                aliases = [a.lower() for a in (s.aliases or [])]
                canonical_lower = s.name.lower()
                registry[canonical_lower] = {
                    "id": s.id,
                    "canonical_name": s.name,
                    "category": s.category,
                    "aliases": aliases
                }
        return registry

    def normalize_skill_name(self, raw_name: str) -> Optional[Tuple[str, str]]:
        """
        Normalizes a raw skill name into (canonical_name, category) if matched.
        """
        clean = raw_name.strip().lower()
        clean = re.sub(r'[\.\-\_\s]+', ' ', clean).strip()

        registry = self.get_canonical_skill_registry()

        # 1. Direct match on canonical name
        for can_lower, data in registry.items():
            if clean == can_lower or clean == re.sub(r'[\.\-\_\s]+', ' ', can_lower).strip():
                return data["canonical_name"], data["category"]

        # 2. Match on aliases
        for can_lower, data in registry.items():
            for alias in data["aliases"]:
                clean_alias = re.sub(r'[\.\-\_\s]+', ' ', alias).strip()
                if clean == clean_alias:
                    return data["canonical_name"], data["category"]

        return None

    def extract_skills_from_text(self, text: str) -> SkillExtractionResponse:
        """
        Extracts and normalizes technical skills from free-form text or resume content.
        Uses exact matching, alias lookup, and regex word-boundary scanning.
        """
        if not text:
            return SkillExtractionResponse(extracted_skills=[], raw_text_length=0, count=0)

        registry = self.get_canonical_skill_registry()
        extracted: Dict[str, ExtractedSkill] = {}
        text_lower = text.lower()

        # Build search patterns for all canonicals and their aliases
        for can_lower, data in registry.items():
            canonical_name = data["canonical_name"]
            category = data["category"]
            
            # Check canonical name with word boundary
            escaped_can = re.escape(can_lower)
            # handle special chars in C++, C#, etc.
            if "++" in can_lower or "#" in can_lower:
                pattern = r'(?:^|[\s,;/\(\)\[\]])' + escaped_can + r'(?:$|[\s,;/\(\)\[\]])'
            else:
                pattern = r'\b' + escaped_can + r'\b'

            if re.search(pattern, text_lower):
                extracted[canonical_name] = ExtractedSkill(
                    original_term=can_lower,
                    canonical_name=canonical_name,
                    category=category,
                    confidence=0.95,
                    matched_via="exact_canonical"
                )
                continue

            # Check aliases
            for alias in data["aliases"]:
                escaped_alias = re.escape(alias)
                if "++" in alias or "#" in alias:
                    alias_pat = r'(?:^|[\s,;/\(\)\[\]])' + escaped_alias + r'(?:$|[\s,;/\(\)\[\]])'
                else:
                    alias_pat = r'\b' + escaped_alias + r'\b'

                if re.search(alias_pat, text_lower):
                    extracted[canonical_name] = ExtractedSkill(
                        original_term=alias,
                        canonical_name=canonical_name,
                        category=category,
                        confidence=0.90,
                        matched_via="alias"
                    )
                    break

        results = list(extracted.values())
        return SkillExtractionResponse(
            extracted_skills=results,
            raw_text_length=len(text),
            count=len(results)
        )
