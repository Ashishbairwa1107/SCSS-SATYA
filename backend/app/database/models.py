import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.core.constants import (
    ExaminationStatus,
    FindingStatus,
    ReviewStatus,
    IntegrityStatus,
    AuditEventType,
)

def utc_now():
    return datetime.now(timezone.utc)

class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_reference = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    purpose = Column(String(255), nullable=True)
    evidence_source = Column(String(255), nullable=True)
    investigator = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    examinations = relationship("Examination", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), unique=True, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    detected_format = Column(String(50), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    color_mode = Column(String(50), nullable=True)
    sha256_hash = Column(String(64), nullable=False, index=True)
    ingestion_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_specimen = Column(Boolean, default=False, nullable=False)
    specimen_type = Column(String(50), nullable=True)
    storage_path = Column(String(512), nullable=False)

    # Relationships
    case = relationship("Case", back_populates="evidence_items")
    examinations = relationship("Examination", back_populates="evidence", cascade="all, delete-orphan")
    verifications = relationship("IntegrityVerification", back_populates="evidence", cascade="all, delete-orphan")


class Examination(Base):
    __tablename__ = "examinations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    evidence_id = Column(String(36), ForeignKey("evidence.id"), nullable=False, index=True)
    status = Column(String(50), default=ExaminationStatus.PENDING.value, nullable=False)
    failure_reason = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    case = relationship("Case", back_populates="examinations")
    evidence = relationship("Evidence", back_populates="examinations")
    analysis_result = relationship("AnalysisResult", back_populates="examination", uselist=False, cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="examination", cascade="all, delete-orphan")
    review = relationship("ExaminerReview", back_populates="examination", uselist=False, cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="examination", cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    examination_id = Column(String(36), ForeignKey("examinations.id"), unique=True, nullable=False, index=True)
    metadata_json = Column(Text, nullable=True)
    ela_artifact_path = Column(String(512), nullable=True)
    ela_scale = Column(Integer, nullable=True)
    ela_quality = Column(Integer, nullable=True)
    ela_format_supported = Column(Boolean, default=False, nullable=False)
    ela_notes = Column(Text, nullable=True)
    rgb_statistics_json = Column(Text, nullable=True)
    spatial_noise_json = Column(Text, nullable=True)
    calculated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    examination = relationship("Examination", back_populates="analysis_result")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    examination_id = Column(String(36), ForeignKey("examinations.id"), nullable=False, index=True)
    finding_key = Column(String(100), nullable=False)
    indicator_name = Column(String(255), nullable=False)
    status = Column(String(50), default=FindingStatus.INCONCLUSIVE.value, nullable=False)
    observed_evidence = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    significance = Column(Text, nullable=False)
    limitations = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    examination = relationship("Examination", back_populates="findings")


class ExaminerReview(Base):
    __tablename__ = "examiner_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    examination_id = Column(String(36), ForeignKey("examinations.id"), unique=True, nullable=False, index=True)
    examiner_name = Column(String(100), nullable=False)
    organization = Column(String(200), nullable=True)
    qualification = Column(String(255), nullable=True)
    credential_status = Column(String(50), default="UNVERIFIED", nullable=False)
    qualitative_notes = Column(Text, nullable=True)
    checklist_responses_json = Column(Text, nullable=True)
    review_status = Column(String(50), default=ReviewStatus.PENDING_REVIEW.value, nullable=False)
    examiner_opinion = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    examination = relationship("Examination", back_populates="review")


class IntegrityVerification(Base):
    __tablename__ = "integrity_verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String(36), ForeignKey("evidence.id"), nullable=False, index=True)
    expected_hash = Column(String(64), nullable=False)
    recomputed_hash = Column(String(64), nullable=False)
    status = Column(String(50), default=IntegrityStatus.UNVERIFIED.value, nullable=False)
    verified_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    details = Column(Text, nullable=True)

    # Relationships
    evidence = relationship("Evidence", back_populates="verifications")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False)
    case_id = Column(String(36), nullable=True, index=True)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    examination_id = Column(String(36), ForeignKey("examinations.id"), nullable=False, index=True)
    report_format = Column(String(20), nullable=False)  # "PDF" or "JSON"
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    generated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    examination = relationship("Examination", back_populates="reports")
