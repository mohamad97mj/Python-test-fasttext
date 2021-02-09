from model import Model
from settings import Settings

if __name__ == '__main__':
    Settings.config_settings()
    bio_model = Model()
    bio_model.train_supervised(auto=True, save=True, duration=15)
    # bio_model.load_model()
    bio_model.test()
    bio_model.predict_all()
    bio_model.save_results()


print("hello")
