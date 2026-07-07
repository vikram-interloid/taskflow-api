from fastapi import Depends, FastAPI

from app.api.database.db_config import get_db

app = FastAPI()

@app.get('/')
def home():
    return {
       'message':'Welcome to TaskFlow-Api'
    }
    
    
@app.get('/test-db')
def testdb(db = Depends(get_db)):
    return {
        'message':'DB Connected'
    }