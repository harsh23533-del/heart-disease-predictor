"""
scanner_engine.py
------------------
Shared logic for the home-page "Smart Scanner": extracting text from an
uploaded PDF/image, pulling out known lab parameters via regex, and
deciding which tool page the person should be routed to.

This re-uses the same PARAMS alias table that Lab_Report.py already
defines, so a value detected here means the same thing it means there.
"""

import re
import io

try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    import pytesseract
    from PIL import Image
    OCR_OK = True
except ImportError:
    OCR_OK = False


# ─── Known lab parameters (same table as Lab_Report.py) ──────────────
PARAMS = {
    "hemoglobin":    {"aliases": ["hemoglobin", "hb", "haemoglobin"],          "min": 12.0, "max": 17.5, "unit": "g/dL"},
    "glucose":       {"aliases": ["glucose", "blood sugar", "fasting sugar"],   "min": 70,   "max": 100,  "unit": "mg/dL"},
    "hba1c":         {"aliases": ["hba1c", "glycated", "a1c"],                  "min": 4.0,  "max": 5.7,  "unit": "%"},
    "creatinine":    {"aliases": ["creatinine", "serum creatinine"],            "min": 0.6,  "max": 1.2,  "unit": "mg/dL"},
    "urea":          {"aliases": ["urea", "blood urea", "bun"],                 "min": 7,    "max": 20,   "unit": "mg/dL"},
    "cholesterol":   {"aliases": ["cholesterol", "total cholesterol"],          "min": 0,    "max": 200,  "unit": "mg/dL"},
    "triglycerides": {"aliases": ["triglycerides", "tg"],                       "min": 0,    "max": 150,  "unit": "mg/dL"},
    "hdl":           {"aliases": ["hdl", "hdl cholesterol"],                    "min": 40,   "max": 999,  "unit": "mg/dL"},
    "ldl":           {"aliases": ["ldl", "ldl cholesterol"],                    "min": 0,    "max": 100,  "unit": "mg/dL"},
    "wbc":           {"aliases": ["wbc", "white blood", "leukocytes"],          "min": 4000, "max": 11000,"unit": "cells/uL"},
    "rbc":           {"aliases": ["rbc", "red blood"],                          "min": 4.2,  "max": 5.9,  "unit": "million/uL"},
    "platelets":     {"aliases": ["platelets", "plt", "thrombocytes"],          "min": 150000,"max":400000,"unit": "cells/uL"},
    "tsh":           {"aliases": ["tsh", "thyroid stimulating"],                "min": 0.4,  "max": 4.0,  "unit": "mIU/L"},
    "sodium":        {"aliases": ["sodium", "na+", "serum sodium"],             "min": 136,  "max": 145,  "unit": "mEq/L"},
    "potassium":     {"aliases": ["potassium", "k+", "serum potassium"],        "min": 3.5,  "max": 5.0,  "unit": "mEq/L"},
    "calcium":       {"aliases": ["calcium", "serum calcium"],                  "min": 8.5,  "max": 10.5, "unit": "mg/dL"},
    "uric acid":     {"aliases": ["uric acid", "urate"],                        "min": 3.5,  "max": 7.2,  "unit": "mg/dL"},
    "bilirubin":     {"aliases": ["bilirubin", "total bilirubin"],              "min": 0.2,  "max": 1.2,  "unit": "mg/dL"},
    "sgpt":          {"aliases": ["sgpt", "alt", "alanine"],                    "min": 7,    "max": 40,   "unit": "U/L"},
    "sgot":          {"aliases": ["sgot", "ast", "aspartate"],                  "min": 10,   "max": 40,   "unit": "U/L"},
    # extra params not in Lab_Report.py's table, needed for routing to
    # Heart_Disease.py and Blood_Kidney.py specifically
    "egfr":          {"aliases": ["egfr", "gfr"],                               "min": 90,   "max": 999,  "unit": "mL/min"},
    "bp":            {"aliases": ["blood pressure", "resting bp", "trestbps", "bp"], "min": 90, "max": 120, "unit": "mmHg"},
    "max_hr":        {"aliases": ["max heart rate", "thalach", "heart rate"],   "min": 60,   "max": 220,  "unit": "bpm"},
}


# ─── Text extraction ───────────────────────────────────────────────

def extract_text_from_pdf(file) -> str:
    if not PDF_OK:
        return ""
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception:
        return ""


def extract_text_from_image(file) -> str:
    """OCR an uploaded image. Requires pytesseract AND the tesseract-ocr
    system binary to be installed on the host (pip install alone is not
    enough). Returns '' if either is missing or OCR fails."""
    if not OCR_OK:
        return ""
    try:
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    except Exception:
        return ""


def extract_text(uploaded_file) -> str:
    """Dispatch based on file extension."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return extract_text_from_image(uploaded_file)
    elif name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return ""


# ─── Parameter detection ───────────────────────────────────────────

def find_value(text: str, aliases) -> float | None:
    text_lower = text.lower()
    for alias in aliases:
        pattern = rf"{re.escape(alias)}[\s:=\|]+([0-9]+\.?[0-9]*)"
        match = re.search(pattern, text_lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


def detect_parameters(text: str) -> dict:
    """Returns {param_name: value} for every recognized parameter found."""
    found = {}
    for param, info in PARAMS.items():
        val = find_value(text, info["aliases"])
        if val is not None:
            found[param] = val
    return found


# ─── Routing ────────────────────────────────────────────────────────

HEART_PARAMS = {"bp", "cholesterol", "max_hr"}
KIDNEY_BLOOD_PARAMS = {"creatinine", "urea", "egfr", "hemoglobin", "wbc", "platelets"}

# free-text symptom keywords as a fallback when no numeric values are found
HEART_KEYWORDS = ["chest pain", "angina", "palpitation", "heart", "cardiac"]
KIDNEY_KEYWORDS = ["kidney", "creatinine", "dialysis", "urea", "renal"]
SKIN_KEYWORDS = ["rash", "itch", "skin", "lesion", "acne", "eczema"]


def decide_route(found_params: dict, raw_text: str) -> str:
    """
    Decide which page to send the user to, based on which parameters
    were detected. Falls back to keyword matching on raw text if no
    recognized numeric parameters were found at all.

    Returns one of: 'Heart_Disease', 'Blood_Kidney', 'Lab_Report'
    """
    heart_hits = len(HEART_PARAMS & found_params.keys())
    kidney_hits = len(KIDNEY_BLOOD_PARAMS & found_params.keys())

    if heart_hits == 0 and kidney_hits == 0:
        text_lower = raw_text.lower()
        if any(k in text_lower for k in HEART_KEYWORDS):
            return "Heart_Disease"
        if any(k in text_lower for k in KIDNEY_KEYWORDS):
            return "Blood_Kidney"
        # generic lab panel detected (e.g. cholesterol alone, hba1c, etc.)
        # or nothing at all -> let Lab_Report.py do the full breakdown
        return "Lab_Report"

    return "Heart_Disease" if heart_hits >= kidney_hits else "Blood_Kidney"


def build_prefill(found_params: dict) -> dict:
    """
    Map detected raw parameter values onto the actual widget keys used
    in Heart_Disease.py and Blood_Kidney.py, clamped to each widget's
    slider range so a wild OCR misread can't push a slider out of bounds.
    """
    prefill = {}

    if "bp" in found_params:
        prefill["trestbps"] = max(90, min(200, found_params["bp"]))
    if "cholesterol" in found_params:
        prefill["chol"] = max(100, min(600, found_params["cholesterol"]))
    if "max_hr" in found_params:
        prefill["thalach"] = max(60, min(220, found_params["max_hr"]))

    if "hemoglobin" in found_params:
        prefill["hemoglobin"] = max(4.0, min(20.0, found_params["hemoglobin"]))
    if "wbc" in found_params:
        # PARAMS table stores wbc in cells/uL; Blood_Kidney slider is in x10^3/uL
        val = found_params["wbc"]
        val = val / 1000 if val > 100 else val
        prefill["wbc"] = max(1.0, min(30.0, val))
    if "platelets" in found_params:
        val = found_params["platelets"]
        val = val / 1000 if val > 1000 else val
        prefill["platelets"] = max(50.0, min(800.0, val))
    if "creatinine" in found_params:
        prefill["creatinine"] = max(0.4, min(15.0, found_params["creatinine"]))
    if "urea" in found_params:
        prefill["bun"] = max(5.0, min(100.0, found_params["urea"]))
    if "egfr" in found_params:
        prefill["egfr"] = max(5.0, min(120.0, found_params["egfr"]))

    return prefill