from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.app.virustotal_client import VirusTotalClient
from backend.app.dataset_loader import UNSWDatasetLoader
from backend.app.schemas import (
    VirusTotalURLScanRequest,
    VirusTotalFileScanRequest,
    VirusTotalScanResponse,
    NetworkThreatRequest,
    NetworkThreatResponse,
    ExplanationItem,
    BatchAnalysisRequest,
    BatchAnalysisResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global clients
vt_client = None
dataset_loader = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global vt_client, dataset_loader

    # Startup
    logger.info("Initializing VirusTotal client...")
    vt_client = VirusTotalClient()

    logger.info("Initializing UNSW-NB15 dataset loader...")
    dataset_loader = UNSWDatasetLoader(data_dir="./data/unsw")

    yield

    # Shutdown
    if vt_client:
        vt_client.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="VulNweb Threat Detection API",
    description="Real-time cyber threat surveillance system with UNSW-NB15 and VirusTotal",
    version="0.2.0",
    lifespan=lifespan
)

# CORS Configuration for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "0.2.0",
        "services": {
            "virustotal": "configured" if vt_client and vt_client.client else "not configured",
            "dataset_loader": "ready" if dataset_loader else "not ready"
        }
    }

# VirusTotal Endpoints
@app.post("/threats/virustotal/scan-url", response_model=VirusTotalScanResponse)
async def scan_url_virustotal(request: VirusTotalURLScanRequest):
    """Scan a URL with VirusTotal API"""
    if not vt_client or not vt_client.client:
        raise HTTPException(status_code=503, detail="VirusTotal service not available")

    logger.info(f"Scanning URL: {request.url}")
    result = vt_client.get_url_analysis(request.url)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return VirusTotalScanResponse(
        scan_target=result.get("url"),
        scan_type="url",
        malicious_detections=result.get("malicious_detections", 0),
        total_vendors=result.get("total_vendors", 0),
        detection_ratio=result.get("detection_ratio", "0/0"),
        threat_level=result.get("threat_level", "unknown"),
        additional_data={"categories": result.get("categories", {})}
    )

@app.post("/threats/virustotal/scan-file", response_model=VirusTotalScanResponse)
async def scan_file_virustotal(request: VirusTotalFileScanRequest):
    """Scan a file hash with VirusTotal API"""
    if not vt_client or not vt_client.client:
        raise HTTPException(status_code=503, detail="VirusTotal service not available")

    logger.info(f"Scanning file hash: {request.file_hash}")
    result = vt_client.scan_file_hash(request.file_hash)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return VirusTotalScanResponse(
        scan_target=result.get("file_hash"),
        scan_type="file",
        malicious_detections=result.get("malicious_detections", 0),
        total_vendors=result.get("total_vendors", 0),
        detection_ratio=result.get("detection_ratio", "0/0"),
        threat_level=result.get("threat_level", "unknown"),
        additional_data={"file_type": result.get("file_type", "unknown")}
    )

# UNSW-NB15 Network Threat Detection Endpoints
@app.post("/threats/network/analyze", response_model=NetworkThreatResponse)
async def analyze_network_threat(request: NetworkThreatRequest):
    """
    Analyze network traffic for threats using UNSW-NB15 model

    This endpoint would integrate with trained ML model for network threat detection
    """
    logger.info(f"Analyzing network flow: {request.source_ip} -> {request.destination_ip}")

    # Placeholder for ML model prediction
    # In a real implementation, this would use a trained XGBoost model
    threat_score = calculate_threat_score_mock(request)

    threat_level = "safe"
    if threat_score < 0.3:
        threat_level = "safe"
    elif threat_score < 0.7:
        threat_level = "suspicious"
    else:
        threat_level = "critical"

    return NetworkThreatResponse(
        threat_score=threat_score * 100,
        threat_level=threat_level,
        confidence=0.92,
        attack_category=None,
        explanation=[
            ExplanationItem(reason="Unusual packet ratio detected", importance=0.35),
            ExplanationItem(reason="High byte transfer rate", importance=0.28),
            ExplanationItem(reason="Port combination suspicious", importance=0.22)
        ]
    )

@app.get("/threats/dataset/info")
async def get_dataset_info():
    """Get information about UNSW-NB15 dataset"""
    if not dataset_loader:
        raise HTTPException(status_code=503, detail="Dataset loader not available")

    return {
        "dataset": "UNSW-NB15",
        "source": "https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15",
        "features": 47,
        "attack_categories": [
            "Analysis", "Backdoor", "DoS", "Exploits",
            "Fuzzers", "Generic", "Reconnaissance", "Shellcode", "Worms"
        ],
        "total_samples": 2540047,
        "benign_samples": 2218761,
        "attack_samples": 321276
    }

@app.post("/threats/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_threats(request: BatchAnalysisRequest):
    """
    Perform batch analysis of URLs, file hashes, and network flows
    """
    logger.info("Starting batch threat analysis")

    results = []
    critical_count = 0
    suspicious_count = 0

    # Analyze URLs with VirusTotal
    if request.urls:
        for url in request.urls:
            if vt_client and vt_client.client:
                vt_result = vt_client.get_url_analysis(url)
                if "error" not in vt_result:
                    results.append({
                        "type": "url",
                        "target": url,
                        "result": vt_result
                    })
                    if vt_result.get("threat_level") == "critical":
                        critical_count += 1
                    elif vt_result.get("threat_level") == "suspicious":
                        suspicious_count += 1

    # Analyze file hashes with VirusTotal
    if request.file_hashes:
        for file_hash in request.file_hashes:
            if vt_client and vt_client.client:
                vt_result = vt_client.scan_file_hash(file_hash)
                if "error" not in vt_result:
                    results.append({
                        "type": "file",
                        "target": file_hash,
                        "result": vt_result
                    })
                    if vt_result.get("threat_level") == "critical":
                        critical_count += 1
                    elif vt_result.get("threat_level") == "suspicious":
                        suspicious_count += 1

    # Analyze network flows
    if request.network_flows:
        for flow in request.network_flows:
            threat_score = calculate_threat_score_mock(flow)
            threat_level = "safe"
            if threat_score < 0.3:
                threat_level = "safe"
            elif threat_score < 0.7:
                threat_level = "suspicious"
                suspicious_count += 1
            else:
                threat_level = "critical"
                critical_count += 1

            results.append({
                "type": "network_flow",
                "target": f"{flow.source_ip}:{flow.source_port} -> {flow.destination_ip}:{flow.destination_port}",
                "result": {"threat_level": threat_level, "threat_score": threat_score * 100}
            })

    return BatchAnalysisResponse(
        total_items=len(results),
        threats_detected=len([r for r in results if r["result"].get("threat_level") in ["suspicious", "critical"]]),
        critical_count=critical_count,
        suspicious_count=suspicious_count,
        results=results
    )

@app.get("/threats/download-dataset")
async def download_unsw_dataset():
    """Download UNSW-NB15 dataset from Kaggle"""
    if not dataset_loader:
        raise HTTPException(status_code=503, detail="Dataset loader not available")

    success = dataset_loader.download_kaggle_dataset()

    if success:
        return {"status": "success", "message": "Dataset download initiated"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to download dataset. Ensure Kaggle API credentials are configured."
        )

def calculate_threat_score_mock(request: NetworkThreatRequest) -> float:
    """
    Mock calculation of threat score based on network features

    In production, this would use a trained ML model
    """
    score = 0.0

    # Higher scores for suspicious ports
    if request.destination_port in [4444, 5555, 8888, 9999, 31337]:
        score += 0.3

    # Check packet ratios
    if request.total_fwd_packets > 0:
        ratio = request.total_bwd_packets / request.total_fwd_packets
        if ratio > 10 or ratio < 0.1:
            score += 0.2

    # Long duration with low packets
    if request.flow_duration > 1000 and (request.total_fwd_packets + request.total_bwd_packets) < 10:
        score += 0.25

    return min(score, 1.0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)