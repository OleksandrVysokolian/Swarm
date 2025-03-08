import cv2
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from supabase import create_client

url="https://kcuzslepwnwfkkkomlfv.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjdXpzbGVwd253Zmtra29tbGZ2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA0NzM1NjksImV4cCI6MjA1NjA0OTU2OX0.GfnoOmNE0SDKQ0oUOhexOo7r2uD-FarmdYNUuEEdidU"

supabase = create_client(url, key)

def scan_qr():
    image = st.camera_input("Show QR code")

    if image is not None:
        bytes_data = image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        detector = cv2.QRCodeDetector()

        data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

        st.write("Here!")
        st.write(data)

def decoder(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(gray_img)

    if data:
        points = np.array(bbox[0], np.int32)
        points = points.reshape((-1, 1, 2))
        cv2.polylines(image, [points], True, (0, 255, 0), 3)

        x, y, w, h = cv2.boundingRect(points)
        string = "Data: " + data
        cv2.putText(image, string, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        print("QR Code: " + data)
        return data  # Return the QR code data
    return None

def scan_qr_code():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()

    barcode_data = None  # Store barcode result

    while barcode_data is None:  # Continue scanning until a barcode is detected
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Could not read frame.")
            break

        barcode_data = decoder(frame)  # Assuming decoder is defined to extract QR code

        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.draw()
        plt.pause(0.001)
        ax.clear()

    cap.release()
    plt.close()
    return barcode_data  # Return the scanned QR code data

def get_customer_balance(customer_id):
    """Retrieve customer balance from Supabase"""
    result = supabase.table("customers").select("balance").eq("id", customer_id).execute()
    if result.data:
        return result.data[0]["balance"]
    return None # Return None for both if no data is found.

def get_customer_saved(customer_id):
    """Retrieve customer saved value from Supabase"""
    result = supabase.table("customers").select("saved").eq("id", customer_id).execute()
    if result.data:
        return result.data[0]["saved"]
    return None # Return None for both if no data is found.

def update_customer_balance(customer_id, new_balance, new_saved):
    """Update customer balance in Supabase"""
    supabase.table("customers").update({"balance": new_balance, "saved": new_saved}).eq("id", customer_id).execute()

def get_merchant_balance(merchant_id):
    """Retrieve merchant balance from Supabase"""
    result = supabase.table("merchants").select("balance").eq("id", merchant_id).execute()
    if result.data:
        return result.data[0]["balance"]
    return None

def update_merchant_balance(customer_id, new_balance):
    """Update merchant balance in Supabase"""
    supabase.table("merchants").update({"balance": new_balance}).eq("id", customer_id).execute()
