"""VirusTotal API Integration"""
import vt
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VirusTotalClient:
    """Client for VirusTotal API interactions"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VIRUSTOTAL_API_KEY")
        if not self.api_key:
            logger.warning("VirusTotal API key not configured")
            self.client = None
        else:
            self.client = vt.Client(self.api_key)

    def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Scan a URL using VirusTotal

        Returns:
            Dict with scan results and threat information
        """
        if not self.client:
            return {"error": "VirusTotal API not configured"}

        try:
            url_obj = self.client.scan_url(url)
            return {
                "url": url,
                "scan_id": url_obj.id,
                "last_analysis": url_obj.last_analysis_date,
                "threat_level": self._calculate_threat_level(url_obj)
            }
        except Exception as e:
            logger.error(f"Error scanning URL {url}: {str(e)}")
            return {"error": str(e), "url": url}

    def get_url_analysis(self, url: str) -> Dict[str, Any]:
        """
        Get analysis results for a URL

        Returns:
            Dict with detailed analysis results
        """
        if not self.client:
            return {"error": "VirusTotal API not configured"}

        try:
            url_id = vt.url_to_id(url)
            url_obj = self.client.get_object("/urls/{url_id}", url_id=url_id)

            stats = url_obj.last_analysis_stats
            detections = stats.get("malicious", 0)
            total = sum(stats.values())

            return {
                "url": url,
                "malicious_detections": detections,
                "total_vendors": total,
                "detection_ratio": f"{detections}/{total}",
                "threat_level": self._calculate_threat_level(url_obj),
                "categories": url_obj.categories if hasattr(url_obj, 'categories') else {}
            }
        except Exception as e:
            logger.error(f"Error getting URL analysis for {url}: {str(e)}")
            return {"error": str(e), "url": url}

    def scan_file_hash(self, file_hash: str) -> Dict[str, Any]:
        """
        Check file hash against VirusTotal database

        Returns:
            Dict with file threat information
        """
        if not self.client:
            return {"error": "VirusTotal API not configured"}

        try:
            file_obj = self.client.get_object(f"/files/{file_hash}")

            stats = file_obj.last_analysis_stats
            detections = stats.get("malicious", 0)
            total = sum(stats.values())

            return {
                "file_hash": file_hash,
                "malicious_detections": detections,
                "total_vendors": total,
                "detection_ratio": f"{detections}/{total}",
                "threat_level": self._calculate_threat_level(file_obj),
                "file_type": file_obj.type_description if hasattr(file_obj, 'type_description') else "unknown"
            }
        except Exception as e:
            logger.error(f"Error scanning file hash {file_hash}: {str(e)}")
            return {"error": str(e), "file_hash": file_hash}

    @staticmethod
    def _calculate_threat_level(vt_object) -> str:
        """
        Calculate threat level based on malicious detections

        Returns:
            Threat level: "safe", "suspicious", or "critical"
        """
        try:
            stats = vt_object.last_analysis_stats
            detections = stats.get("malicious", 0)
            total = sum(stats.values())

            if total == 0:
                return "unknown"

            ratio = detections / total

            if ratio == 0:
                return "safe"
            elif ratio < 0.3:
                return "suspicious"
            else:
                return "critical"
        except:
            return "unknown"

    def close(self):
        """Close the VirusTotal client"""
        if self.client:
            self.client.close()
