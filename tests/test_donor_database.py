#!/usr/bin/env python3
"""
Test suite for DonorDatabase
"""
import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from donor_database import DonorDatabase, Donor

def run_tests():
    logging.basicConfig(level=logging.INFO)
    db = DonorDatabase()
    results = []
    # Test: Add and retrieve donor
    donor = Donor(name="Test Donor", type="individual", region="Europe", country="Germany", focus_areas=["science"], website="https://test.org")
    donor_id = db.add_donor(donor)
    results.append(f"Add donor returned ID: {donor_id}")
    retrieved = db.get_donor_by_id(donor_id)
    results.append(f"Retrieved donor name: {retrieved.name if retrieved else 'None'}")
    # Test: Search
    found = db.search_donors("Test Donor")
    results.append(f"Search found: {len(found)} donors")
    # Test: Matching
    matches = db.find_matching_donors(["science"], "research")
    results.append(f"Matching donors for 'science/research': {len(matches)}")
    # Test: Update website info (mocked, will not error if site unreachable)
    updated = db.update_donor_website_info(donor_id)
    results.append(f"Update donor website info: {updated}")
    # Test: Get all donors
    all_donors = db.get_donors()
    results.append(f"Total donors in DB: {len(all_donors)}")
    # Test: Save donor match
    if all_donors:
        db.save_donor_match(all_donors[0].id, 999, 0.9, "Test match reason")
        matches = db.get_donor_matches(999)
        results.append(f"Donor matches for opportunity 999: {len(matches)}")
    return results

if __name__ == "__main__":
    output = run_tests()
    with open(os.path.join(os.path.dirname(__file__), '../logs/test_donor_database_output.txt'), 'w') as f:
        for line in output:
            print(line)
            f.write(line + '\n')
