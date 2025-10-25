import time

def parse_snort_alert(line: str) -> dict:
    """
    Parse a single line from snort.alert.fast
    """
    try:
        parts = line.split("[Classification:")
        msg_part = parts[0].split("]")[2].strip()
        classification = parts[1].split("]")[0].strip()
        priority = int(parts[1].split("Priority:")[1].split("]")[0].strip())
        src_dst = line.split("{")[1].split("}")[1].strip()
        src, dst = src_dst.split("->")
        return {
            "raw": line.strip(),
            "msg": msg_part,
            "classification": classification,
            "priority": priority,
            "src": src.strip(),
            "dst": dst.strip(),
            "timestamp": time.time()
        }
    except Exception:
        return None

