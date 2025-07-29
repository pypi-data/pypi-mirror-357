import subprocess

def get_cpu_usage():
    applescript = '''
    set cpuLine to do shell script "top -l 1 -n 0 | grep 'CPU usage'"
    set cpuParts to paragraphs of (do shell script "echo " & quoted form of cpuLine & " | sed 's/CPU usage: //; s/%//g' | tr ',' '\\n'")
    set cpuNumbers to {}
    repeat with part in cpuParts
        set numberText to word 1 of part
        set end of cpuNumbers to (numberText as real)
    end repeat
    return cpuNumbers
    '''
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript failed: {result.stderr.strip()}")
    
    # result.stdout will be something like: {5.18, 9.51, 85.3}
    # Parse it to Python list of floats:
    output = result.stdout.strip().strip('{}').split(',')
    return [float(x) for x in output]

# Example usage
if __name__ == "__main__":
    print(get_cpu_usage())
