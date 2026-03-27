#!/usr/bin/env python3
"""
Script Splitter Utility
Splits a full debate script into multiple parts for serialized video content.
Each part contains 2 turns (one from each philosopher).
"""

import json
import sys
from pathlib import Path

def split_script(input_path="output_script.json", turns_per_part=2, output_dir="parts"):
    """
    Split a debate script into multiple parts.
    
    Args:
        input_path: Path to the full script JSON
        turns_per_part: Number of turns per part (default 2 = one exchange)
        output_dir: Directory to save part files
    
    Returns:
        List of part file paths
    """
    # Load the full script
    with open(input_path, 'r') as f:
        full_data = json.load(f)
    
    script = full_data["script"]
    total_turns = len(script)
    
    # Calculate number of parts
    num_parts = (total_turns + turns_per_part - 1) // turns_per_part
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    part_files = []
    
    print(f"\n{'='*60}")
    print(f"SPLITTING DEBATE SCRIPT")
    print(f"{'='*60}")
    print(f"Total turns: {total_turns}")
    print(f"Turns per part: {turns_per_part}")
    print(f"Number of parts: {num_parts}")
    print(f"{'='*60}\n")
    
    # Split into parts
    for part_num in range(num_parts):
        start_idx = part_num * turns_per_part
        end_idx = min(start_idx + turns_per_part, total_turns)
        
        part_script = script[start_idx:end_idx]
        
        # Create part data structure
        part_data = {
            "topic": full_data["topic"],
            "author_a": full_data["author_a"],
            "author_b": full_data["author_b"],
            "part_number": part_num + 1,
            "total_parts": num_parts,
            "script": part_script
        }
        
        # Save part file
        part_filename = f"output_script_part{part_num + 1}.json"
        part_filepath = output_path / part_filename
        
        with open(part_filepath, 'w') as f:
            json.dump(part_data, f, indent=2)
        
        part_files.append(str(part_filepath))
        
        # Print part info
        print(f"PART {part_num + 1}/{num_parts}:")
        print(f"  File: {part_filepath}")
        print(f"  Turns: {len(part_script)}")
        for i, turn in enumerate(part_script):
            speaker = turn["speaker"]
            text_preview = turn["text"][:60] + "..." if len(turn["text"]) > 60 else turn["text"]
            print(f"    Turn {start_idx + i + 1}: {speaker}")
            print(f"      → {text_preview}")
        print()
    
    print(f"{'='*60}")
    print(f"✓ Created {num_parts} part files in '{output_dir}/'")
    print(f"{'='*60}\n")
    
    return part_files

def main():
    """Command-line interface for script splitting."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Split debate scripts into multiple parts for video series"
    )
    parser.add_argument(
        "--input",
        default="output_script.json",
        help="Input script JSON file (default: output_script.json)"
    )
    parser.add_argument(
        "--turns-per-part",
        type=int,
        default=2,
        help="Number of turns per part (default: 2)"
    )
    parser.add_argument(
        "--output-dir",
        default="parts",
        help="Output directory for part files (default: parts/)"
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found!")
        sys.exit(1)
    
    # Split the script
    part_files = split_script(
        input_path=args.input,
        turns_per_part=args.turns_per_part,
        output_dir=args.output_dir
    )
    
    print("Part files created:")
    for pf in part_files:
        print(f"  • {pf}")

if __name__ == "__main__":
    main()