"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

# Allowed values exactly as per README.md
VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agents.md enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Default State ("Other" + "Standard" + NEEDS_REVIEW flag for ambiguity)
    category = "Other"
    priority = "Standard"
    reason = "Complaint lacks details to determine the specific issue."
    flag = "NEEDS_REVIEW"
    
    # 1. Determine Priority (Severity Blindness Rule)
    # "Priority must be 'Urgent' if the description explicitly mentions or implies immediate danger..."
    if any(kw in desc for kw in URGENT_KEYWORDS):
        priority = "Urgent"

    # 2. Determine Category (Taxonomy Drift & Hallucination Rule)
    # "Category must be exactly one of the fixed enum values..."
    if "pothole" in desc:
        category = "Pothole"
        reason = f"Mentioned 'pothole', mapped to {category}."
        flag = ""
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
        reason = f"Mentioned 'flood' or 'water', mapped to {category}."
        flag = ""
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
        reason = f"Mentioned 'light' or 'dark', mapped to {category}."
        flag = ""
    elif "waste" in desc or "garbage" in desc or "smell" in desc or "animal" in desc:
        category = "Waste"
        reason = f"Mentioned 'waste', 'garbage' or 'animal', mapped to {category}."
        flag = ""
    elif "noise" in desc or "music" in desc:
        category = "Noise"
        reason = f"Mentioned 'noise' or 'music', mapped to {category}."
        flag = ""
    elif "crack" in desc or "sink" in desc or "surface" in desc:
        category = "Road Damage"
        reason = f"Mentioned 'crack' or 'sink', mapped to {category}."
        flag = ""
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason = f"Mentioned 'heritage', mapped to {category}."
        flag = ""
    elif "heat" in desc:
        category = "Heat Hazard"
        reason = f"Mentioned 'heat', mapped to {category}."
        flag = ""
    elif "drain" in desc or "block" in desc:
        category = "Drain Blockage"
        reason = f"Mentioned 'drain' or 'block', mapped to {category}."
        flag = ""
    elif "manhole" in desc:
        category = "Road Damage"
        reason = f"Mentioned 'manhole', mapped to {category}."
        flag = ""

    # Ensure output strictly matches schema
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Ignore null rows gracefully
                    if not row.get("complaint_id"):
                        continue
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    # Robust error handling for bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error processing row: {str(e)}",
                        "flag": "ERROR"
                    })
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_path}'")
        sys.exit(1)
        
    # Write to target CSV
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for res in results:
            writer.writerow(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
