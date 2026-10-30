from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class MetadataField(BaseModel):
    tag: str
    label: str
    value: Optional[str] = None
    status: str  # "Present", "Missing", "Unreadable", "Unsupported"
    is_software_trace: bool = False
    is_sensitive: bool = False
    notes: Optional[str] = None

class MetadataCategory(BaseModel):
    name: str
    fields: list[MetadataField]

class ELAResponse(BaseModel):
    format_supported: bool
    quality: Optional[int] = None
    scale: Optional[int] = None
    artifact_id: Optional[str] = None
    artifact_url: Optional[str] = None
    grayscale_artifact_url: Optional[str] = None
    notes: str
    mean_difference: Optional[float] = None
    max_difference: Optional[float] = None
    residual_std: Optional[float] = None
    limitation_statement: str

class RGBChannelStat(BaseModel):
    mean: float
    std_dev: float
    min: float
    max: float
    median: float

class HistogramBin(BaseModel):
    bin: int
    r: int
    g: int
    b: int

class RGBStatisticsResponse(BaseModel):
    red: RGBChannelStat
    green: RGBChannelStat
    blue: RGBChannelStat
    histogram: list[HistogramBin]
    total_pixels_sampled: int
    sampling_method: str
    interpretation: str

class SpatialNoiseResponse(BaseModel):
    laplacian_variance: float
    sobel_gradient_mean: float
    high_freq_noise_sigma: float
    method_name: str
    interpretation: str
    limitations: str

class FindingResponse(BaseModel):
    id: str
    finding_key: str
    indicator_name: str
    status: str  # "No Indicator Detected", "Indicator Observed", "Inconclusive"
    observed_evidence: str
    explanation: str
    significance: str
    limitations: str
    recommended_action: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)
