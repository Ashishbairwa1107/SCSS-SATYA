import io
import json
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Examination, AnalysisResult, Evidence
from app.schemas.analysis import ELAResponse, RGBStatisticsResponse, SpatialNoiseResponse

router = APIRouter(prefix="/examinations", tags=["Analysis"])

@router.get("/{examination_id}/ela", response_model=ELAResponse)
def get_ela_analysis(examination_id: str, db: Session = Depends(get_db)):
    """Retrieve Error Level Analysis (ELA) parameters, residual stats, and artifact exhibits."""
    ex = db.query(Examination).filter(Examination.id == examination_id).first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examination not found.")

    ar = ex.analysis_result
    if not ar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis result not yet generated.")

    artifact_url = f"/api/evidence/artifacts/{ar.ela_artifact_path}" if ar.ela_artifact_path else None
    
    # Check grayscale artifact
    gray_url = None
    if ar.ela_artifact_path and "heatmap" in ar.ela_artifact_path:
        gray_file = ar.ela_artifact_path.replace("heatmap", "gray")
        gray_url = f"/api/evidence/artifacts/{gray_file}"

    # Parse metrics from ela_notes if present
    mean_diff = None
    max_diff = None
    res_std = None
    if ar.ela_notes:
        m_mean = re.search(r"Mean residual difference:\s*(\d+(?:\.\d+)?)", ar.ela_notes)
        m_std = re.search(r"standard deviation:\s*(\d+(?:\.\d+)?)", ar.ela_notes)
        m_max = re.search(r"maximum residual:\s*(\d+(?:\.\d+)?)", ar.ela_notes)
        if m_mean:
            mean_diff = float(m_mean.group(1))
        if m_std:
            res_std = float(m_std.group(1))
        if m_max:
            max_diff = float(m_max.group(1))

    return ELAResponse(
        format_supported=ar.ela_format_supported,
        quality=ar.ela_quality,
        scale=ar.ela_scale,
        artifact_id=ar.ela_artifact_path,
        artifact_url=artifact_url,
        grayscale_artifact_url=gray_url,
        notes=ar.ela_notes or "ELA analysis completed.",
        mean_difference=mean_diff,
        max_difference=max_diff,
        residual_std=res_std,
        limitation_statement=(
            "ELA reflects compression residual error rates across DCT blocks. High contrast edges and textural elements "
            "naturally create higher error. Residual variance alone does not substantiate composite insertion."
        )
    )

@router.get("/{examination_id}/statistics")
def get_image_statistics(examination_id: str, db: Session = Depends(get_db)):
    """Retrieve RGB color distribution, 32-bin histograms, and spatial noise measurements."""
    ex = db.query(Examination).filter(Examination.id == examination_id).first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examination not found.")

    ar = ex.analysis_result
    if not ar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis result not yet generated.")

    rgb_obj = json.loads(ar.rgb_statistics_json) if ar.rgb_statistics_json else {}
    spatial_obj = json.loads(ar.spatial_noise_json) if ar.spatial_noise_json else {}

    return {
        "rgb_statistics": rgb_obj,
        "spatial_noise": spatial_obj,
        "dimensions": {
            "width": ex.evidence.width,
            "height": ex.evidence.height,
            "color_mode": ex.evidence.color_mode,
            "detected_format": ex.evidence.detected_format,
        }
    }
