# AI Cybersecurity Audit Review PoC

This project is a proof-of-concept that analyzes cybersecurity audit reports (~100 pages) using AI. It detects formatting and clarity issues, checks for jargon and missing information, provides improvement recommendations, and extracts vulnerabilities.

> Note: This project is modular. The page-level analysis and the vulnerability extraction are done in separate scripts and not as a single complete process.

## Project Status
- Page-level analysis ✅
- Formatting and clarity checks ✅
- Jargon and missing information checks ✅
- Vulnerability extraction ✅
- Global vulnerability review ✅
- Vulnerability alignment check ⚠️ (unfinished)

## How It does
1. Run the page-level analysis script to analyze each page for formatting, clarity, jargon, and missing information and to  Generate improvement recommendations based on the page analysis.   
2. Run the vulnerability extraction script to extract vulnerabilities from the report.  
3. Run the revueGlobaleVuln script to perform a global review of all vulnerabilities.
## Features
- Detect formatting errors
- Identify clarity issues
- Check for jargon and missing information
- Provide recommendations for improvements
- Extract detected vulnerabilities
- Perform a global vulnerability review
