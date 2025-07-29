
"""
rockford investigates suspicious shit.

Copyright (C) 2025  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

import email
import re
from zoneinfo import ZoneInfo

from dateutil import parser as dp


def main():
    with open('input/smf_email.text') as fd:
        msg = email.message_from_file(fd)

    rcvd = msg.get_all('Received')

    date_ms = (
        r'('
            # Match OPTIONAL DAY and DATE ['Wed, ']'09 Apr 2025' OR
            r'(([A-Za-z]{3},\s)?\d{1,2}\s[A-Za-z]{3}\s\d{4})|'
            # Match DATE '2025-04-09'
            r'(\d{4}(-\d{2}){2})'
        r')'
        # Match SPACE and TIME ' 00:01:42'
        r'\s(\d{2}:\d{2}:\d{2})'
        # Match OPTIONAL Microsecond as a decimal number '.209405196'
        r'(\.\d+)?'
        # Match SPACE and UTC offset in the form ±HHMM ' -0400'
        r'\s((\+|-)\d{4})'
    )

    for r in rcvd:
        date_search = re.search(date_ms, r)
        if date_search:
            d = dp.parse(date_search.group()).astimezone(ZoneInfo('America/New_York'))
            print(f"Received: {d}")
