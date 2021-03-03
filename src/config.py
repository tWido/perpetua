
DB_USER = 'perp'
DB_PWD = 'iWantGoodSchool'
DB_URL = '127.0.0.1'
DB_NAME = 'perpetua'

ALLOWED_COLUMNS = {
  'reviews': ['id', 'school_id', 'student_id', 'completed', 'created'],
  'schools': ['id', 'name', 'region', 'town', 'language', 'level', 'type', 'distance'],  # distance is counted column
  'tokens': ['token']
}

RATED = ['teachers', 'peers', 'food', 'dorms', 'subjects', 'building', 'options', 'activities']
