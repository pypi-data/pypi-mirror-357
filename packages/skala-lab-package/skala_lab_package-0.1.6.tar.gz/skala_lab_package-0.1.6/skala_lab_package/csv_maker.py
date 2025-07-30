import os
import csv
import json

def generate_csv_with_column_prompt(input_folder, column_list, output_csv_name):
    global file_names, paths, list_extracted_features, updated_col_names
    file_names, paths, list_extracted_features = [], [], []
    updated_col_names = ["file_name", "file_path"] + column_list

    print("Starting CSV generation...")
    print(f"Reading JSON config: {input_folder}")

    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"JSON file not found: {input_folder}")

    with open(input_folder, "r") as f:
        config = json.load(f)
        root_dir = config.get("path")

    print(f"Target folder from JSON: {root_dir}")
    if not os.path.isdir(root_dir):
        raise Exception(f"Invalid directory path: {root_dir}")

    output_csv = output_csv_name if output_csv_name.endswith(".csv") else output_csv_name + ".csv"
    output_path = os.path.join(root_dir, output_csv)

    print(f"Output CSV will be saved as: {output_path}")

    # Extract folder name metadata
    for entry in os.listdir(root_dir):
        full_path = os.path.join(root_dir, entry)
        if os.path.isdir(full_path):
            file_names.append(entry)
            paths.append(full_path)
            parts = entry.split("_")
            list_extracted_features.append(parts)

    print(f"Found {len(list_extracted_features)} folders to process.")

    if not list_extracted_features:
        raise Exception("No subdirectories found in the target folder.")

    # Validate column list
    possible_inputs = ["cell_line", "condition", "dish", "channel_type", "cell_type", "resolution"]
    for name in column_list:
        if name not in possible_inputs:
            raise Exception(f"Invalid column name: {name}")

    selected_indexes = [possible_inputs.index(col) for col in column_list]

    # Process each row
    for i, parts in enumerate(list_extracted_features):
        row = parts

        if "dish" in column_list:
            dish_idx = column_list.index("dish")
            dish_val = row[dish_idx].upper()
            if "DISH" in dish_val:
                row[dish_idx] = dish_val.replace("DISH", "")
            else:
                raise Exception(f"Invalid 'dish' format in row {i}: {dish_val}")

        if "channel_type" in column_list:
            ct_idx = column_list.index("channel_type")
            row[ct_idx] = infer_channel_type(row[ct_idx])

        filtered_row = [file_names[i], paths[i]] + [row[j] for j in selected_indexes]

        if len(filtered_row) != len(updated_col_names):
            print(f"Row length mismatch at index {i}: {filtered_row}")

        list_extracted_features[i] = filtered_row

    print(f"Writing {len(list_extracted_features)} rows to CSV...")

    try:
        with open(output_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(updated_col_names)
            writer.writerows(list_extracted_features)
    except Exception as e:
        print(f"Error writing CSV: {e}")
        raise

    print(f"CSV saved to: {output_path}")
    return output_path


# --- Optional utility: Get channel types even if not requested ---
def get_channel_type_list(root_dir):
	channel_types = []
	for entry in os.listdir(root_dir):
		full_path = os.path.join(root_dir, entry)
		if os.path.isdir(full_path):
			parts = entry.split("_")
			found = False
			for part in parts:
				ct = infer_channel_type(part)
				if ct in ("f", "n"):
					channel_types.append(ct)
					found = True
					break
			if not found:
				channel_types.append("unknown")
	return channel_types

# --- Helper to clean channel type ---
def infer_channel_type(value: str) -> str:
	value = value.lower()
	if 'f' in value:
		return 'f'
	elif 'n' in value:
		return 'n'
	else:
		return 'unknown'
