#!/usr/bin/env python3
"""
Simple YAML Endpoint Extractor

This script reads the master_kg_api.yaml file and prints all endpoints.

Usage:
    python extract_from_yaml.py
"""

import re
from pathlib import Path


def find_yaml_file():
    """Find the master_kg_api.yaml file."""
    yaml_files = [
        'master_kg_api.yaml',
        '../master_kg_api.yaml',
        '../../master_kg_api.yaml',
        'backend/master_kg_api.yaml'
    ]
    
    for file_path in yaml_files:
        if Path(file_path).exists():
            return file_path
    return None


def extract_endpoints_simple(file_path):
    """Extract endpoints using simple text parsing."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    endpoints = []
    lines = content.split('\n')
    
    current_path = None
    current_method = None
    in_responses = False
    
    for i, line in enumerate(lines):
        # Find path
        path_match = re.match(r'^\s*([/][^:]+):\s*$', line)
        if path_match:
            current_path = path_match.group(1)
            current_method = None
            in_responses = False
            continue
        
        # Find method
        method_match = re.match(r'^\s*(get|post|put|patch|delete):\s*$', line)
        if method_match and current_path:
            current_method = method_match.group(1).upper()
            endpoints.append({
                'path': current_path,
                'method': current_method,
                'has_responses': False
            })
            in_responses = False
            continue
        
        # Check for responses
        if current_method and 'responses:' in line:
            in_responses = True
            endpoints[-1]['has_responses'] = True
            continue
        
        # Reset when indentation decreases
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            in_responses = False
    
    return endpoints


def main():
    """Main function."""
    yaml_file = find_yaml_file()
    if not yaml_file:
        print("Error: master_kg_api.yaml file not found")
        return
    
    print(f"Reading: {yaml_file}")
    endpoints = extract_endpoints_simple(yaml_file)
    
    print(f"\nFound {len(endpoints)} endpoints:\n")
    
    # Group by path
    paths = {}
    for endpoint in endpoints:
        if endpoint['path'] not in paths:
            paths[endpoint['path']] = []
        paths[endpoint['path']].append(endpoint)
    
    # Print all endpoints
    for path, path_endpoints in paths.items():
        print(f"=== {path} ===")
        for endpoint in path_endpoints:
            response_status = "✅" if endpoint['has_responses'] else "❌"
            print(f"  {endpoint['method']} - Response Body: {response_status}")
        print()
    
    # Summary
    total = len(endpoints)
    with_responses = len([ep for ep in endpoints if ep['has_responses']])
    without_responses = total - with_responses
    
    print("=== SUMMARY ===")
    print(f"Total endpoints: {total}")
    print(f"With response body: {with_responses}")
    print(f"Without response body: {without_responses}")
    
    if without_responses > 0:
        print(f"\nEndpoints missing response body:")
        for endpoint in endpoints:
            if not endpoint['has_responses']:
                print(f"  {endpoint['method']} {endpoint['path']}")


if __name__ == '__main__':
    main()
