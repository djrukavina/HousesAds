from realestate_monitor.fetch import _looks_blocked

VALID_NJUSKALO_PAGE = (
    "<html><head><title>Prodaja stanova Trešnjevka - Jug</title></head><body>"
    + "x" * 2000
    + '<script>ssconf("c1", "https://cdn.perfdrive.com/aperture/aperture.js");</script>'
    + "<script>isRecaptchaFeatureEnabled</script>"
    + "</body></html>"
)

CAPTCHA_PAGE = (
    "<html><head><title>ShieldSquare Captcha</title></head><body>"
    + "x" * 2000
    + "</body></html>"
)


def test_normal_njuskalo_page_is_not_blocked() -> None:
    assert not _looks_blocked(VALID_NJUSKALO_PAGE)


def test_captcha_interstitial_is_blocked() -> None:
    assert _looks_blocked(CAPTCHA_PAGE)
