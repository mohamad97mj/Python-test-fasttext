from bio_model import BioModel
from settings import Settings

if __name__ == '__main__':
    Settings.config_settings()
    bio_model = BioModel()
    # bio_model.load_model()
    # bio_model.train_supervised()
    bio_model.train_supervised(auto=True, save=True)
    bio_model.test()
    bio_model.predict_all()
    bio_model.save_results()
