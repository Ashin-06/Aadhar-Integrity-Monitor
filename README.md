# 🛡️ Aadhaar Integrity Monitoring System (AIMS)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B.svg)](https://streamlit.io/)

A comprehensive AI-driven system designed to detect and monitor integrity issues in India's Aadhaar ecosystem. Built for the **UIDAI Data Hackathon 2026**.

## 🎯 Project Overview

This system uses machine learning and advanced data processing to identify three major types of integrity issues:
1.  **Ghost Villages:** Highly suspicious clusters of enrolments in uninhabited or sparsely populated areas.
2.  **Correction Syndicates:** Targeted demographic updates (mobile, address) that indicate fraudulent account takeovers.
3.  **Compliance Gaps:** Anomalous biometric update patterns that bypass standard security protocols.

## 🚀 Key Features

*   **Massive Data Processing:** Scripts optimized to handle millions of rows across multiple datasets.
*   **AI Fraud Detection:** Machine learning models that detect anomalies and suspicious patterns.
*   **Interactive Dashboard:** A professional Streamlit-based interface to visualize fraud hotspots and system health.
*   **Risk Classification:** Automated grading of PIN codes and districts (Low, Medium, High, Extreme risk).

## 📂 Repository Structure

```text
Aadhar_Integrity_Monitoring_System/
├── 📄 production_data_processor.py   # STEP 1: Aggregation & Cleaning
├── 📄 unified_fraud_detector.py      # STEP 2: ML-based Fraud Detection
├── 📄 interactive_dashboard.html     # STEP 3: Visual Results (Static)
├── 📄 requirements.txt               # Required Python libraries
├── 📄 .gitignore                     # Prevents large data uploads
├── 📄 sample_biometric_data.csv      # Demo data (Biometric)
├── 📄 sample_demographic_data.csv    # Demo data (Demographic)
├── 📄 sample_enrolment_data.csv      # Demo data (Enrolment)
└── 📄 README.md                      # Documentation (You are here)
```

## 🛠️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Aadhar-Integrity-Monitor.git
    cd Aadhar-Integrity-Monitor
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚡ Execution Guide

### Step 1: Data Processing
Processes raw enrolment, demographic, and biometric data.
```bash
python production_data_processor.py
```

### Step 2: Fraud Detection
Runs the ML models and generates anomaly reports.
```bash
python unified_fraud_detector.py
```

### Step 3: View Results
Open the `interactive_dashboard.html` in your browser or run the Streamlit dashboard (if available).

## 👥 The Team

*   **Ashin** - ML Engineer & Lead Developer
*   **Omika Singh** - Frontend/UI Designer
*   **Niranjana Vinod** - Data Cleaning Specialist
*   **Jobsy Shaji** - Technical Documentation & Report

## ⚖️ License
This project is built for the UIDAI Data Hackathon 2026. All rights reserved by the team.

---
*Developed for the UIDAI Hackathon 2026*
