import re, traceback

# =========================================================
# PATTERNS
# =========================================================

BROWSER_PATTERNS = [
    ("Edge", re.compile(r"edg(?:e|a)?/([\d\.]+)", re.I)),
    ("Opera", re.compile(r"(?:opera|opr)/([\d\.]+)", re.I)),
    ("Samsung Browser", re.compile(r"samsungbrowser/([\d\.]+)", re.I)),
    ("Chrome iOS", re.compile(r"crios/([\d\.]+)", re.I)),
    ("Firefox iOS", re.compile(r"fxios/([\d\.]+)", re.I)),
    ("Chrome", re.compile(r"chrome/([\d\.]+)", re.I)),
    ("Firefox", re.compile(r"firefox/([\d\.]+)", re.I)),
    ("Safari", re.compile(r"version/([\d\.]+).*safari", re.I)),
]

OS_PATTERNS = [
    ("Windows", re.compile(r"windows nt ([\d\.]+)", re.I)),
    ("Android", re.compile(r"android ([\d\.]+)", re.I)),
    ("iOS", re.compile(r"os ([\d_]+) like mac os x", re.I)),
    ("MacOS", re.compile(r"mac os x ([\d_\.]+)", re.I)),
    ("Linux", re.compile(r"linux", re.I)),
]


def clean_value(value, default="-"):
    try:
        if value is None:
            return default

        value = str(value).replace('"', '').strip()

        if not value:
            return default

        return value

    except Exception:
        print(traceback.format_exc())
        return default


def get_client_hints(headers: dict):
    try:
        return {
            "sec_ch_ua": headers.get("Sec-CH-UA", ""),

            "platform": clean_value(
                headers.get("Sec-CH-UA-Platform")
            ),

            "mobile": clean_value(
                headers.get("Sec-CH-UA-Mobile")
            ),

            "platform_version": clean_value(
                headers.get("Sec-CH-UA-Platform-Version")
            ),
        }

    except Exception:
        print(traceback.format_exc())

        return {
            "sec_ch_ua": "",
            "platform": "-",
            "mobile": "-",
            "platform_version": "-",
        }


def parse_browser(ua: str, sec_ch_ua: str):
    try:
        browser = "Other"
        browser_version = "-"

        # Prioritas Client Hints
        if sec_ch_ua:

            matches = re.findall(
                r'"([^"]+)";v="(\d+)"',
                sec_ch_ua
            )

            for name, ver in matches:

                if name not in (
                    "Chromium",
                    "Not-A.Brand"
                ):
                    browser = name
                    browser_version = ver
                    break

        # Fallback User-Agent
        if browser == "Other":

            for name, pattern in BROWSER_PATTERNS:

                match = pattern.search(ua)

                if match:
                    browser = name

                    if match.groups():
                        browser_version = match.group(1)

                    break

        return browser, browser_version

    except Exception:
        print(traceback.format_exc())
        return "Other", "-"


def parse_os(ua: str, platform: str, platform_version: str):
    try:
        os_name = "Other"
        os_version = "-"

        # Prioritas Client Hints
        if platform != "-":
            os_name = platform
            os_version = platform_version

        # Fallback User-Agent
        else:
            for name, pattern in OS_PATTERNS:

                match = pattern.search(ua)

                if match:
                    os_name = name

                    if match.groups():
                        os_version = (
                            match.group(1)
                            .replace("_", ".")
                        )

                    break

        return os_name, os_version

    except Exception:
        print(traceback.format_exc())
        return "Other", "-"


def parse_device(ua: str, mobile: str):
    try:
        ua_lower = ua.lower()

        if mobile == "?1":
            return "Mobile"

        elif (
            "ipad" in ua_lower
            or "tablet" in ua_lower
        ):
            return "Tablet"

        elif (
            "mobile" in ua_lower
            or "iphone" in ua_lower
            or "android" in ua_lower
        ):
            return "Mobile"

        return "Desktop"

    except Exception:
        print(traceback.format_exc())
        return "Unknown"


# =========================================================
# MAIN PARSER
# =========================================================

def parse_user_agent(ua: str, headers: dict = None):
    try:
        headers = headers or {}

        if not ua or ua == "-":
            ua = ""

        # =====================================================
        # CLIENT HINTS
        # =====================================================

        hints = get_client_hints(headers)

        # =====================================================
        # BROWSER
        # =====================================================

        browser, browser_version = parse_browser(
            ua,
            hints["sec_ch_ua"]
        )

        # =====================================================
        # OS
        # =====================================================

        os_name, os_version = parse_os(
            ua,
            hints["platform"],
            hints["platform_version"]
        )

        # =====================================================
        # DEVICE
        # =====================================================

        device = parse_device(
            ua,
            hints["mobile"]
        )

        # =====================================================
        # RESULT
        # =====================================================

        return {
            "browser": browser,
            "browser_version": browser_version,

            "os": os_name,
            "os_version": os_version,

            "device": device,
        }

    except Exception:
        print(traceback.format_exc())

        return {
            "browser": "Error",
            "browser_version": "-",

            "os": "Error",
            "os_version": "-",

            "device": "Unknown",
        }