#!/usr/bin/env python3

# Required dependencies
# pip install pydub

import os
from pathlib import Path
import subprocess

def convert_m4a_to_wav():
    try:
        # Define source and target directories
        source_dir = Path('voice_juan')
        target_dir = Path('tortoise/voices/juan')
        
        print(f"Looking for .m4a files in: {source_dir.absolute()}")
        
        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"Target directory created/verified: {target_dir.absolute()}")
        
        # Check if source directory exists
        if not source_dir.exists():
            print(f"Error: Source directory '{source_dir.absolute()}' not found!")
            return
        
        # List all m4a files
        m4a_files = list(source_dir.glob('*.m4a'))
        print(f"Found {len(m4a_files)} .m4a files")
        
        # Process all m4a files
        for idx, m4a_file in enumerate(m4a_files):
            try:
                # Generate output filename
                output_file = target_dir / f'juan_{idx}.wav'
                
                print(f"\nProcessing {m4a_file.name} -> {output_file.name}")
                
                # Construct ffmpeg command
                # -y: overwrite output file
                # -i: input file
                # -ac 1: convert to mono
                # -ar 22050: set sample rate to 22050 Hz
                cmd = [
                    './ffmpeg',
                    '-y',
                    '-i', str(m4a_file.absolute()),
                    '-ac', '1',
                    '-ar', '22050',
                    str(output_file.absolute())
                ]
                
                # Run ffmpeg
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"Successfully converted {m4a_file.name} to {output_file.name}")
                else:
                    print(f"Error converting {m4a_file.name}:")
                    print(result.stderr)
                
            except Exception as e:
                print(f"Error processing {m4a_file.name}:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print("Traceback:")
                import traceback
                traceback.print_exc()
        
        print(f"\nConversion complete! {len(m4a_files)} files processed.")
        
    except Exception as e:
        print("An unexpected error occurred:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("Traceback:")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    convert_m4a_to_wav() 