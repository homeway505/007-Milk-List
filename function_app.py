import azure.functions as func
import pandas as pd
from io import BytesIO
import base64
import logging


def process_excel(excel_data):
    # Load the Excel file content into a DataFrame, specifying columns A and C
    df = pd.read_excel(excel_data, engine='openpyxl', skiprows=4, usecols="A,C")

    # Data processing steps
    df.dropna(how='all', inplace=True)  # Remove rows where both A and C are NaN
    df = df.ffill()  # Fill NaN in A from the previous row if C is not NaN
    df = df.drop_duplicates(subset=df.columns[1])  # Remove duplicates based on column C
    df = df.dropna(subset=[df.columns[1]])  # Drop rows where column C is NaN
    df = df.reset_index(drop=True)  # Reset index

    # logging.info(df)
    # print(df)

    # Convert DataFrame to JSON string
    df_json = df.to_json(orient="records")

    return df_json

# Initialize the Function App with anonymous authentication
app = func.FunctionApp()

@app.function_name("milk_list")

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Attempt to retrieve file content from the request parameter or body
        file_content_encoded = req.params.get('FileContent')
        if not file_content_encoded:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                file_content_encoded = req_body.get('FileContent')

        if file_content_encoded is None:
            logging.error('File content not found.')

            return func.HttpResponse(
                "Please pass the file content in the request body as 'FileContent'.",
                status_code=400
            )

        logging.debug('Processing an Excel file.')

        # Decode the base64 file content to binary
        file_content = base64.b64decode(file_content_encoded)
        excel_data = BytesIO(file_content)
        df_json = process_excel(excel_data)

        # Return the JSON string in the response with application/json mimetype
        return func.HttpResponse(df_json, status_code=200, mimetype="application/json")

        # For demonstration, return a success message
        # return func.HttpResponse("Excel file processed successfully.", status_code=200)

    except Exception as e:
        logging.error(f"Failed to process the Excel file: {e}")
        return func.HttpResponse(
            f"Error processing the Excel file: {str(e)}",
            status_code=500
        )


@app.blob_trigger(arg_name="myblob", path="daily-file", connection="milklist_STORAGE") 
def BlobTrigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    
    # Read the blob content into a BytesIO object
    excel_data = BytesIO(myblob.read())

    df_json = process_excel(excel_data)


# @app.route(route="http_trigger2", auth_level=func.AuthLevel.FUNCTION)
# def http_trigger2(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )