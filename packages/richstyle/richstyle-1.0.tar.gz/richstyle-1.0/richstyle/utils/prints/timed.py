from ...colors.character_color_map import character_color_map
from ...core.combine_text import combine_text
from ...colors.presets import presets
from ...styles.bold import bold

from datetime import datetime

_COLOR = presets.antique_white

def timed_print(*text: str):
    """Prints a message prefixed with the current time (H:M:S) on the left."""
    
    now = datetime.now()
    current_time_str = now.strftime("%I:%M%p")

    combined_text = combine_text(*text)
    prefix = bold(_COLOR(current_time_str))

    print(f"{prefix} {combined_text}")
