from gopro_overlay.font import load_font


def load_test_font():
    try:
        return load_font("LXGWWenKai-Light.ttf")
    except OSError:
        return load_font("trebuc.ttf")

