import firebase_admin
from firebase_admin import credentials, db
def main():
    # Replace these values with your Firebase Admin SDK JSON file path, database URL, and Google Sheet details
    credential_path = 'def main():
    # Replace these values with your Firebase Admin SDK JSON file path, database URL, and Google Sheet details
    credential_path = '/content/drive/MyDrive/MR JSON/employee-analytics-test-default-rtdb-export.json'
    database_url = 'https://employee-analytics-test-default-rtdb.firebaseio.com'
    spreadsheet_key = '1ZW7XIcnDg20oQ_h2ClO7izBdqPaNW-KzRqGCqt1wmKE'  # Replace with the actual spreadsheet key

    # 1. Initialize Firebase app
    app = initialize_firebase_app(credential_path, database_url)

    # 2. Get a reference to the desired database path (Replace with the actual path)
    data = retrieve_data_from_firebase(app, '/')

    # Print the retrieved data
    print(data)

if _name_ == "_main_":
    main()'
    database_url = 'https://employee-analytics-test-default-rtdb.firebaseio.com/'
    spreadsheet_key = '1ZW7XIcnDg20oQ_h2ClO7izBdqPaNW-KzRqGCqt1wmKE'  # Replace with the actual spreadsheet key

    # 1. Initialize Firebase app
    app = initialize_firebase_app(credential_path, database_url)

    # 2. Get a reference to the desired database path (Replace with the actual path)
    data = retrieve_data_from_firebase(app, '/')

    # Print the retrieved data
    print(data)

if _name_ == "_main_":
    main()