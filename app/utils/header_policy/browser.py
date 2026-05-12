from .hardening  import build_hardening
from .csp        import build_csp
from .transport  import build_transport
from .isolation  import build_isolation
from .cache      import build_cache


""" FILE CORS DAN API BELUM DI TERAPKAN KE SINI """

def browser_privacy(response):
    """
    Orchestrator header keamanan dan privasi browser.
    Dipanggil sekali per response untuk halaman HTML / aset browser.
    Setiap file menangani satu kelompok header — tidak ada overlap.

    Urutan eksekusi:
      1. hardening.py  → X-Content-Type-Options, X-Frame-Options,
                         X-XSS-Protection, Referrer-Policy, Permissions-Policy
      2. csp.py        → Content-Security-Policy
      3. transport.py  → Strict-Transport-Security
      4. isolation.py  → Cross-Origin-Opener-Policy,
                         Cross-Origin-Embedder-Policy,
                         Cross-Origin-Resource-Policy
      5. cache.py      → Cache-Control

    Untuk API endpoint, gunakan build_api() dari api.py — bukan fungsi ini.
    """

    build_hardening(response)
    build_csp(response)
    build_transport(response)
    build_isolation(response)
    build_cache(response)

    return response