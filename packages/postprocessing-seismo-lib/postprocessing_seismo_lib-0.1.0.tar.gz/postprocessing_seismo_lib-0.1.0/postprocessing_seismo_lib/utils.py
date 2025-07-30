import json
import pandas as pd
import xmltodict
import traceback

def convert_file_to_json(input_file: str,
                         output_file: str,
                         id: str,
                         event_file: str = None,
                         pick_file: str = None,
                         error_log_file: str = None):
    """
    Auto-detect format (csv, quakeml, arcout) and convert to standard JSON response.

    Parameters:
        input_file (str): Main input file (for quakeml or arcout).
        output_file (str): Output JSON filename.
        id (str): Event ID to use in the JSON.
        event_file (str): (Optional) For CSV: Path to events CSV file.
        pick_file (str): (Optional) For CSV: Path to picks CSV file.
        error_log_file (str): Optional path to write traceback if an error occurs.
    """
    try:
        detected_format = None
        body = None

        # Case 1: CSV — both event_file and pick_file must be provided
        if event_file and pick_file:
            df_events = pd.read_csv(event_file)
            df_picks = pd.read_csv(pick_file)

            events_list = df_events.to_dict(orient="records")
            picks_list = df_picks.to_dict(orient="records")

            for pick in picks_list:
                for key in ["Amplitude", "Filter", "Quality", "Site", "Source"]:
                    if key in pick and not isinstance(pick[key], str):
                        pick[key] = json.dumps(pick[key])

            body = [events_list, picks_list]
            detected_format = "csv"

        # Case 2: Try XML parsing
        elif input_file:
            try:
                with open(input_file, "r") as f:
                    xml_str = f.read()
                body_dict = xmltodict.parse(xml_str)

                extracted_id = (
                    body_dict.get('q:quakeml', {})
                    .get('eventParameters', {})
                    .get('event', {})
                    .get('@ns0:eventid', 'unknown_id')
                )
                id = id or extracted_id
                body = body_dict
                detected_format = "quakeml"

            except Exception:
                # Fallback to arcout if XML parsing fails
                with open(input_file, "r") as f:
                    lines = f.readlines()
                body = [lines]
                detected_format = "arcout"

        else:
            raise ValueError("No input_file or CSV files provided.")

        # Build final response
        response = {
            "status": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body_meta": {
                "id": id,
                "format": detected_format
            },
            "body": body
        }

        with open(output_file, "w") as f:
            json.dump(response, f, indent=2)

        print(f"[✓] Format: {detected_format} — Saved output to {output_file}")

    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"[✗] Error encountered: {e}")
        if error_log_file:
            with open(error_log_file, "w") as f:
                f.write(error_msg)
            print(f"[!] Error logged to {error_log_file}")
        else:
            print("[!] No error_log_file specified; error not saved.")


def build_message(body, id_str, format_str):
    """
    Constructs the full JSON message given body content, ID, and format.
    """
    return {
        "status": 200,
        "headers": {"Content-Type": "application/json"},
        "body_meta": {"id": id_str, "format": format_str},
        "body": body
    }

def extract_body_from_file(filepath):
    """
    Loads a JSON file and returns only the 'body' field.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("body", None)
