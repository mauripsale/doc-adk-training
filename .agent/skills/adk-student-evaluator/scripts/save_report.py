import sys
import os

def append_report(report_content, output_file="student-evaluation-reports.md"):
    try:
        # Check if we are in the root or need to find it
        if not os.path.exists(output_file):
             # Try to go up if needed or create it
             pass
             
        with open(output_file, "a") as f:
            f.write("\n---\n")
            f.write(report_content)
            f.write("\n")
        print(f"Successfully appended report to {output_file}")
    except Exception as e:
        print(f"Error saving report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python save_report.py '<markdown_content>'")
        sys.exit(1)
    append_report(sys.argv[1])
