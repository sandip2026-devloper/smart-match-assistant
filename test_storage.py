from app import create_app
from app.services.document_processor import process_excel
from app.services.record_storage import save_processed_records


app = create_app()


with app.app_context():

    result = process_excel(
        r"uploads\2f8fbef6b7864a728751694e5f68bfbc.xlsx"
    )

    print("Processing:", result["success"])
    print("Records:", result["record_count"])

    if result["success"]:

        saved = save_processed_records(
            document_id=7,
            user_id=1,
            processed_records=result["records"]
        )

        print("Storage:", saved)