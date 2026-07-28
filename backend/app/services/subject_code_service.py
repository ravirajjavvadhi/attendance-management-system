import re
from sqlalchemy.orm import Session
from app.models.erp_academic import Subject

class SubjectCodeService:
    @staticmethod
    def get_display_code(subject: Subject) -> str:
        """Returns explicit code if set by management, else fall back to auto-generated code."""
        if not subject:
            return "N/A"
        if subject.code and subject.code.strip():
            return subject.code.strip().upper()
        if hasattr(subject, 'generated_code') and subject.generated_code and subject.generated_code.strip():
            return subject.generated_code.strip().upper()
        # Last resort fallback for legacy unsynchronized subjects
        words = subject.name.strip().split()
        if len(words) > 1:
            base = "".join(w[0] for w in words if w.isalnum()).upper()[:4]
        else:
            base = re.sub(r'[^A-Za-z0-9]', '', subject.name.upper())[:3]
        return base or "SUB"

    @staticmethod
    def resolve_subject_code(db: Session, tenant_id: int, subject_name: str, explicit_code: str = None) -> dict:
        """
        Generates or validates collision-safe subject codes.
        Returns dict with: {'code': str/None, 'generated_code': str, 'is_auto_generated': bool}
        """
        if explicit_code and explicit_code.strip() and explicit_code.strip().upper() != "NONE":
            clean_code = explicit_code.strip().upper()
            return {
                "code": clean_code,
                "generated_code": clean_code,
                "is_auto_generated": False
            }

        # Handle automatic collision-safe generation
        clean_name = subject_name.strip()
        words = [w for w in re.split(r'\W+', clean_name) if w]
        if len(words) >= 2:
            # Initials of words (e.g., Computer Networks -> CN, Design Analysis Algorithms -> DAA)
            base_prefix = "".join(w[0] for w in words).upper()[:5]
        elif len(words) == 1:
            # First 3 letters (e.g., Aptitude -> APT)
            base_prefix = words[0].upper()[:3]
        else:
            base_prefix = "GEN"

        # Check existing codes in this tenant to prevent collisions
        existing_subjects = db.query(Subject).filter(Subject.tenant_id == tenant_id).all()
        existing_codes = set()
        for s in existing_subjects:
            if s.code:
                existing_codes.add(s.code.upper())
            if hasattr(s, 'generated_code') and s.generated_code:
                existing_codes.add(s.generated_code.upper())

        candidate = base_prefix
        counter = 2
        while candidate in existing_codes:
            if counter <= 9:
                candidate = f"{base_prefix}{counter}" # e.g. CN2, CN3
            else:
                candidate = f"{base_prefix}{counter + 91}" # e.g. CN101, CN102
            counter += 1

        return {
            "code": None,
            "generated_code": candidate,
            "is_auto_generated": True
        }

subject_code_service = SubjectCodeService()
