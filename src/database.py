import os


DATABASE_STORAGE = os.path.join(os.environ['AICV'], 'database')
os.environ['AICV_DATABASE'] = DATABASE_STORAGE

DRIVE_STORAGE = os.path.join(DATABASE_STORAGE, 'drive')


INSTALLED_DATABASES = [DATABASE_STORAGE, DRIVE_STORAGE]


for db in INSTALLED_DATABASES:
    if not os.path.exists(db):
        os.mkdir(db)