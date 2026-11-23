from app.core.config import split_origins


def test_split_origins_trims_and_drops_blanks():
    assert split_origins(" https://finscope.vercel.app , http://localhost:5173, ") == [
        "https://finscope.vercel.app",
        "http://localhost:5173",
    ]
