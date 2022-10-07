import os
from datetime import datetime

import unidecode


def upload_to(instance, filename):
    def make_safe(s):
        def safe_char(c):
            return c if c.isalnum() else "_"

        return unidecode.unidecode("".join(safe_char(c) for c in s).strip(" _"))

    _, file_extension = os.path.splitext(filename)
    safe_filename = (
        make_safe(f'{instance}_{datetime.now().strftime("%Y%m%d-%H%M%S")}')
        + file_extension
    )
    return os.path.join(instance.__class__.__name__, safe_filename)
