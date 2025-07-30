from .tokens import (
    TokenLanguagePack,
    AdditiveConjunctionToken,
    NotSupportedToken,
    IgnoredToken,
    IntervalConjunctionToken,
    PrecisionConjunctionToken,
)


class FrenchTokens(TokenLanguagePack):
    class EtToken(AdditiveConjunctionToken):
        substr = "et"

    class VirguleToken(AdditiveConjunctionToken):
        substr = ","

    class PuisToken(AdditiveConjunctionToken):
        substr = "puis"

    class OuToken(NotSupportedToken):
        substr = "ou"

    class SaufToken(NotSupportedToken):
        substr = "sauf"

    class LeToken(IgnoredToken):
        substr = "le"

    class LesToken(IgnoredToken):
        substr = "les"

    class DuToken(IntervalConjunctionToken):
        substr = "du"
        class_char = "f"

    class DeToken(IntervalConjunctionToken):
        substr = "de"
        class_char = ":"

    class AuToken(IntervalConjunctionToken):
        substr = "au"
        class_char = "o"

    class JusquAuToken(IntervalConjunctionToken):
        substr = "jusqu'au"
        class_char = "o"

    class AToken(PrecisionConjunctionToken):
        substr = "à"
        class_char = "à"

    class DashToken(PrecisionConjunctionToken):
        substr = "-"
        class_char = "-"

    conjunctions = [
        PuisToken,
        DeToken,
        DuToken,
        AuToken,
        JusquAuToken,
        AToken,
        DashToken,
    ]

    ignored_conjunctions = [LeToken, LesToken, EtToken, VirguleToken]

    not_supported = [OuToken, SaufToken]
