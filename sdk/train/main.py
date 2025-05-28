
from sdk.app.logger import Logger
from sdk.train.trainer import Trainer

logger = Logger(__name__)

if __name__ == "__main__":
    try:
        trainer = Trainer()
        trainer.prepare()
        trainer.train()
    except Exception as e:
        logger.error("Unexpected error during training", e)
