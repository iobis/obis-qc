import nose
import logging
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])  # level not applied?
logging.getLogger("asyncio").setLevel(logging.INFO)
logging.getLogger("isodateparser").setLevel(logging.INFO)
logging.getLogger("obisqc.taxonomy").setLevel(logging.INFO)


nose.run()
