from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tensorflow as tf
from tensorflow.keras.preprocessing import image  # type: ignore
import numpy as np
from io import BytesIO
import os
import uvicorn
from PIL import Image
import logging
import mysql.connector
from mysql.connector import Error

app = FastAPI()

class_names = [
    '8', '1', '6', '5', '7',
    '4', '2', '3', '10', '9', '11'
]

# Load the model
model = tf.keras.models.load_model('ml_model.h5')

# Setup logging
logging.basicConfig(level=logging.INFO)

def predict_image(img_array):
    predictions = model.predict(img_array)
    logging.info(f"Raw predictions: {predictions}")
    score = tf.nn.softmax(predictions[0])
    logging.info(f"Softmax score: {score}")
    return {
        "waste_id": int(class_names[np.argmax(score)]),
        "confidence": float(100 * np.max(score))
    }

def store_data_in_mysql(data):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='waste_db',
            user='root',  # replace with your MySQL username
            password=''  # replace with your MySQL password
        )
        if connection.is_connected():
            cursor = connection.cursor()
            sql_insert_query = """INSERT INTO predictions (waste_id, confidence) VALUES (%s, %s)"""
            cursor.execute(sql_insert_query, (data['waste_id'], data['confidence']))
            connection.commit()
            logging.info(f"Data stored in MySQL: {data}")
    except Error as e:
        logging.error(f"Error storing data in MySQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error storing data in MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_waste_details(waste_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='waste_db',
            user='root',  # replace with your MySQL username
            password=''  # replace with your MySQL password
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            sql_select_query = """SELECT name, description, management, processing FROM waste WHERE id = %s"""
            cursor.execute(sql_select_query, (waste_id,))
            result = cursor.fetchone()
            return result
    except Error as e:
        logging.error(f"Error fetching data from MySQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data from MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Load image
        img = Image.open(BytesIO(await file.read())).convert('L')  # Convert to grayscale
        img = img.resize((100, 100))  # Resize to match the training image size

        # Preprocess image
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=-1)  # Add channel dimension (1 channel)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array = img_array / 255.0  # Normalize

        # Predict image
        predictions = predict_image(img_array)

        # Store prediction result in MySQL
        store_data_in_mysql(predictions)

        # Fetch waste details
        waste_details = fetch_waste_details(predictions['waste_id'])

        # Return predictions in response
        response = {
            "waste_id": predictions["waste_id"],
            "confidence": predictions["confidence"],
            "name": waste_details["name"],
            "description": waste_details["description"],
            "management": waste_details["management"],
            "processing": waste_details["processing"]
        }
        
        return JSONResponse(content={"predictions": response}, status_code=200)

    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3000)
