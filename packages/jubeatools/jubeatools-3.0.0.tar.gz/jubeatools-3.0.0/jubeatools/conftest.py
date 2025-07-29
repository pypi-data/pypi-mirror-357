from datetime import timedelta

from hypothesis import settings

settings.register_profile("ci", deadline=timedelta(seconds=1))
