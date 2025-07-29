import codecs
from .codec_base import MSXIncrementalDecoder
from .codec_jp import MSXJapaneseCodec
from .codec_intl import MSXInternationalCodec
from .codec_br import MSXBrazilianCodec
from ._version import __version__

__all__ = ["__version__", "msx_codec_jp", "msx_codec_intl", "msx_codec_br"]


def make_incremental_decoder(codec_class):
    class _IncrementalDecoder(MSXIncrementalDecoder):
        def __init__(self, errors='strict'):
            super().__init__(codec_class(), errors)
    return _IncrementalDecoder


def msx_charset(name):
    if name.lower() in ('msx-jp', 'msx_jp'):
        codec_class = MSXJapaneseCodec
    elif name.lower() in ('msx-intl', 'msx_intl'):
        codec_class = MSXInternationalCodec
    elif name.lower() in ('msx-br', 'msx_br'):
        codec_class = MSXBrazilianCodec
    else:
        raise LookupError(f"unknown encoding: {name}")

    codec = codec_class()
    return codecs.CodecInfo(
        name=name,
        encode=codec.encode,
        decode=codec.decode,
        incrementalencoder=None,
        incrementaldecoder=make_incremental_decoder(codec_class),
    )


# Register codec
codecs.register(msx_charset)
