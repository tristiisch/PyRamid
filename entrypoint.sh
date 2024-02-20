#!/bin/sh
set -e

# # Define the folder containing secrets
# SECRET_FOLDER=/run/secrets

# # Find and loop through all files in the SECRET_FOLDER
# find "$SECRET_FOLDER" -type f | while read -r file; do

#     # Check if the file is a regular file
#     if [ ! -f "$file" ]; then
#         echo "Skipping non-regular file: $file"
#         continue
#     fi

#     echo "Loading environment variables from file: $file"

#     # Initialize line number counter
#     line_number=0

#     # Read all lines in the file
#     while IFS= read -r line || [ -n "$line" ]; do
#         line_number=$((line_number + 1))

#         # Skip empty lines
#         if [ -z "$line" ]; then
#             echo "Skipping empty line $line_number in $file"
#             continue
#         fi

#         # Skip lines that are misformatted
#         if ! [[ "$line" =~ ^[a-zA-Z_]+[a-zA-Z0-9_]*=.* ]]; then
#             echo "Skipping misformatted line $line_number in $file"
#             continue
#         fi

#         # Export the environment variable
#         export "$line"
# 		echo "DEBUG EXPORT $line"
#     done < "$file"

# 	env
#     echo "Finished loading file: $file"

# done

# echo "Starting application..."

# Start the application
exec "$@"
