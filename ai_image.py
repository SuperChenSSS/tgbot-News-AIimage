import base64
import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv
import datetime
import s3fs

def mount_s3(file_name, data):
    bucket_name = "goimage-chen"
    mount_point = "imgs"
    full_path = f"{bucket_name}/{mount_point}/{file_name}"
    s3 = s3fs.S3FileSystem(anon=False)
    with s3.open(full_path, "wb") as f:
        f.write(data)
        #f.close()
    print(f"File {file_name} uploaded to bucket {bucket_name}/{mount_point}")
    return full_path

def generate_img(command=""):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=command),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "image",
            "text",
        ],
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold="OFF",  # Off
            ),
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = datetime.datetime.now().strftime("%H_%M_%S")
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            full_path = f"{file_name}{file_extension}"
            s3_path = mount_s3(f"{full_path}", inline_data.data)
            print(
                "File "
                f" {inline_data.mime_type} saved "
                f"to {s3_path}"
            )
            return s3_path
        else:
            print(chunk.text)

if __name__ == "__main__":
    #load_dotenv(".terraform/secrets.txt")
    command = input("Type anything:\t")
    full_path = generate_img(command)
    print("Full Path:", full_path)
