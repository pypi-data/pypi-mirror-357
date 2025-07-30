from typing import Any, Dict, List, Optional

def clean_pubsub_message(
    msg:Dict[str, Any],
    enums:Optional[List[str]] = None
) -> Dict[str, Any]:
    for k, v in msg.items():
        # Clean enums
        if isinstance(v, dict) and len(v) == 1:
            only_key = next(iter(v))
            if enums is not None and only_key in enums:
                msg[k] = v[only_key]

        # Clean "map"
        if isinstance(v, dict) and "map" in v and isinstance(v["map"], dict):
            msg[k] = v["map"]

        # Clean "array"
        if isinstance(v, dict) and "array" in v and isinstance(v["array"], list):
            msg[k] = v["array"]

    return msg