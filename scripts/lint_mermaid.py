#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import tempfile

def lint_mermaid_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if not mermaid_blocks:
        return True

    all_valid = True
    for i, block in enumerate(mermaid_blocks):
        with tempfile.NamedTemporaryFile(suffix='.mmd', mode='w', delete=False) as tmp:
            tmp.write(block)
            tmp_path = tmp.name

        try:
            # Use local mmdc if available, else npx
            mmdc_path = os.path.join(os.getcwd(), 'node_modules', '.bin', 'mmdc')
            cmd = [mmdc_path] if os.path.exists(mmdc_path) else ['npx', '-p', '@mermaid-js/mermaid-cli', 'mmdc']
            cmd.extend(['-i', tmp_path, '-o', tmp_path + '.svg'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"Error in {file_path} (block {i+1}):")
                print(result.stderr)
                all_valid = False
            
            # Cleanup SVG
            svg_path = tmp_path + '.svg'
            if os.path.exists(svg_path):
                os.remove(svg_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    return all_valid

def main():
    md_files = []
    for root, _, files in os.walk('.'):
        if 'node_modules' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    success = True
    for md_file in md_files:
        if not lint_mermaid_in_file(md_file):
            success = False

    if not success:
        sys.exit(1)
    print("All Mermaid diagrams are valid!")

if __name__ == "__main__":
    main()
