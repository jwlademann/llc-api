import os


class Config(object):
    DEBUG = False
    LLC_REGISTER_URL = os.getenv('LLC_REGISTER_URL', 'http://localhost:5002')
    LLC_API_URI = os.getenv('LLC_API_URI', 'local-land-charge.data.gov:5001')
    RA_API_URI = os.getenv('RA_API_URI', 'llc-registering-authority.data.gov:5001')
    FIL_API_URI = os.getenv('FIL_API_URI', 'further-information-location.data.gov:5001')
    SP_API_URI = os.getenv('SP_API_URI', 'statutory-provision.data.gov:5001')

    LAND_COMP_ACT_S8 = os.getenv('LAND_COMP_ACT_S8', 'Land Compensation Act 1973 section 8(4)')
    LAND_COMP_ACT_S52 = os.getenv('LAND_COMP_ACT_S52', 'Land Compensation Act 1973 section 52(8)')


class DevelopmentConfig(Config):
    DEBUG = True
    LLC_REGISTER_URL = os.getenv('LLC_REGISTER_URL', 'http://llc-register:5002')


class TestConfig(DevelopmentConfig):
    TESTING = True
