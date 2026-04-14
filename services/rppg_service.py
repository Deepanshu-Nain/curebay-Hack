# ============================================================
# services/rppg_service.py — Remote Photoplethysmography (rPPG)
# ============================================================
# Camera-based, non-invasive vital sign extraction.
# Based on: ArXiv 2508.18787v1 — Face2PPG pipeline.
#
# Extracts from facial video:
#   - Heart Rate (HR) via pulse signal from skin colour changes
#   - Respiratory Rate (RR) via breathing-induced modulation
#   - SpO2 estimation via dual-channel ratio analysis
#
# No hardware sensors needed — works with any smartphone camera.
# ============================================================

import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger

from config import settings


class RPPGService:
    """
    Remote Photoplethysmography vital sign extraction.
    Processes short facial video (10-15 seconds) to estimate HR, RR, SpO2.
    """

    def __init__(self):
        self._face_cascade = None

    def _load_detector(self):
        """Lazy load Haar cascade face detector."""
        if self._face_cascade is None:
            try:
                import cv2
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                self._face_cascade = cv2.CascadeClassifier(cascade_path)
                if self._face_cascade.empty():
                    raise RuntimeError("Failed to load Haar cascade classifier")
                logger.info("rPPG face detector loaded.")
            except ImportError:
                logger.error("opencv-python-headless not installed. Run: pip install opencv-python-headless")
                raise

    def extract_vitals_from_video(self, video_path: str) -> Dict[str, Any]:
        """
        Process a short facial video to extract vital signs.

        Args:
            video_path: Path to video file (mp4, avi, webm)

        Returns:
            Dict with heart_rate_bpm, respiratory_rate_per_min,
            spo2_estimate_pct, signal_quality, method
        """
        import cv2

        self._load_detector()

        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or settings.RPPG_FPS
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        logger.info(f"rPPG processing: {total_frames} frames @ {fps:.0f} fps ({duration:.1f}s)")

        # Collect ROI colour signals from forehead region
        green_signal = []
        red_signal = []
        blue_signal = []
        frames_processed = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Detect face
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
            )

            if len(faces) > 0:
                # Use the largest face
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

                # Extract forehead ROI (top 30% of face region)
                forehead_y = y
                forehead_h = int(h * 0.3)
                forehead_x = x + int(w * 0.2)
                forehead_w = int(w * 0.6)

                roi = frame[forehead_y:forehead_y + forehead_h,
                           forehead_x:forehead_x + forehead_w]

                if roi.size > 0:
                    # Average colour per channel
                    mean_bgr = np.mean(roi, axis=(0, 1))
                    blue_signal.append(mean_bgr[0])
                    green_signal.append(mean_bgr[1])
                    red_signal.append(mean_bgr[2])

            frames_processed += 1

        cap.release()

        # Minimum signal length check
        min_samples = int(fps * 5)  # at least 5 seconds of data
        if len(green_signal) < min_samples:
            logger.warning(f"Insufficient signal: {len(green_signal)} samples (need {min_samples})")
            return {
                "heart_rate_bpm": None,
                "respiratory_rate_per_min": None,
                "spo2_estimate_pct": None,
                "signal_quality": "insufficient",
                "method": "rPPG (camera-based, non-invasive)",
                "duration_seconds": round(duration, 1),
                "error": "Not enough face detections. Ensure face is clearly visible.",
            }

        # Convert to numpy arrays
        green = np.array(green_signal)
        red = np.array(red_signal)
        blue = np.array(blue_signal)

        # Extract vital signs
        hr = self._estimate_heart_rate(green, fps)
        rr = self._estimate_respiratory_rate(green, fps)
        spo2 = self._estimate_spo2(red, blue)

        # Determine signal quality
        quality = "good" if len(green_signal) > fps * 10 else "moderate"
        if len(green_signal) < fps * 7:
            quality = "low"

        result = {
            "heart_rate_bpm": round(hr, 1) if hr else None,
            "respiratory_rate_per_min": round(rr, 1) if rr else None,
            "spo2_estimate_pct": round(spo2, 1) if spo2 else None,
            "signal_quality": quality,
            "method": "rPPG (camera-based, non-invasive)",
            "duration_seconds": round(duration, 1),
        }

        logger.info(f"rPPG result: HR={result['heart_rate_bpm']}, "
                    f"RR={result['respiratory_rate_per_min']}, "
                    f"SpO2={result['spo2_estimate_pct']}%")

        return result

    # ── Signal Processing Methods ──────────────────────────────

    def _bandpass_filter(
        self, signal: np.ndarray, fps: float, low: float, high: float, order: int = 4
    ) -> np.ndarray:
        """Apply Butterworth bandpass filter to signal."""
        from scipy.signal import butter, filtfilt

        nyq = fps / 2.0
        low_norm = max(low / nyq, 0.001)
        high_norm = min(high / nyq, 0.999)

        if low_norm >= high_norm:
            return signal

        b, a = butter(order, [low_norm, high_norm], btype='band')
        # Pad signal to avoid edge effects
        padlen = min(3 * max(len(a), len(b)), len(signal) - 1)
        if padlen < 1:
            return signal
        return filtfilt(b, a, signal, padlen=padlen)

    def _estimate_heart_rate(
        self, signal: np.ndarray, fps: float
    ) -> Optional[float]:
        """
        Estimate heart rate from green channel signal.
        Bandpass: 0.7–4.0 Hz (42–240 bpm range)
        """
        try:
            # Detrend and normalise
            signal = signal - np.mean(signal)
            if np.std(signal) < 1e-6:
                return None
            signal = signal / np.std(signal)

            # Bandpass filter for heart rate range
            filtered = self._bandpass_filter(signal, fps, low=0.7, high=4.0)

            # FFT to find dominant frequency
            n = len(filtered)
            fft_vals = np.abs(np.fft.rfft(filtered))
            freqs = np.fft.rfftfreq(n, d=1.0 / fps)

            # Only consider HR range: 0.7–4.0 Hz
            mask = (freqs >= 0.7) & (freqs <= 4.0)
            if not np.any(mask):
                return None

            fft_hr = fft_vals[mask]
            freqs_hr = freqs[mask]

            # Dominant frequency
            peak_idx = np.argmax(fft_hr)
            hr_hz = freqs_hr[peak_idx]
            hr_bpm = hr_hz * 60.0

            # Sanity check
            if 40 <= hr_bpm <= 200:
                return hr_bpm
            return None

        except Exception as e:
            logger.warning(f"HR estimation failed: {e}")
            return None

    def _estimate_respiratory_rate(
        self, signal: np.ndarray, fps: float
    ) -> Optional[float]:
        """
        Estimate respiratory rate from signal modulation.
        Bandpass: 0.1–0.5 Hz (6–30 breaths/min range)
        """
        try:
            signal = signal - np.mean(signal)
            if np.std(signal) < 1e-6:
                return None
            signal = signal / np.std(signal)

            # Bandpass filter for respiratory range
            filtered = self._bandpass_filter(signal, fps, low=0.1, high=0.5)

            # FFT
            n = len(filtered)
            fft_vals = np.abs(np.fft.rfft(filtered))
            freqs = np.fft.rfftfreq(n, d=1.0 / fps)

            mask = (freqs >= 0.1) & (freqs <= 0.5)
            if not np.any(mask):
                return None

            fft_rr = fft_vals[mask]
            freqs_rr = freqs[mask]

            peak_idx = np.argmax(fft_rr)
            rr_hz = freqs_rr[peak_idx]
            rr_per_min = rr_hz * 60.0

            if 6 <= rr_per_min <= 40:
                return rr_per_min
            return None

        except Exception as e:
            logger.warning(f"RR estimation failed: {e}")
            return None

    def _estimate_spo2(
        self, red: np.ndarray, blue: np.ndarray
    ) -> Optional[float]:
        """
        Estimate SpO2 from red and blue channel ratio.
        Uses the ratio-of-ratios (RoR) method.
        Note: This is an estimation — not clinically calibrated.
        """
        try:
            if len(red) < 10 or len(blue) < 10:
                return None

            # AC/DC ratio for each channel
            red_ac = np.std(red)
            red_dc = np.mean(red)
            blue_ac = np.std(blue)
            blue_dc = np.mean(blue)

            if red_dc < 1e-6 or blue_dc < 1e-6:
                return None

            # Ratio of ratios
            ror = (red_ac / red_dc) / (blue_ac / blue_dc)

            # Empirical SpO2 estimation (simplified linear model)
            # SpO2 ≈ 110 - 25 * RoR (typical calibration curve)
            spo2 = 110.0 - 25.0 * ror

            # Clamp to physiological range
            spo2 = max(70.0, min(100.0, spo2))

            return spo2

        except Exception as e:
            logger.warning(f"SpO2 estimation failed: {e}")
            return None

    def is_available(self) -> bool:
        """Check if rPPG service can operate."""
        if not settings.RPPG_ENABLED:
            return False
        try:
            self._load_detector()
            return True
        except Exception:
            return False


# Singleton
rppg_service = RPPGService()
