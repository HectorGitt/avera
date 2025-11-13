import os
import sys
import uuid
import subprocess
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import tempfile
import shutil

app = FastAPI(
    title="TripoSG: Image to 3D Model Generation",
    description="Upload an image and generate a 3D GLB model using TripoSG.",
)

# Determine the base directory of the TripoSG project
triposg_base_dir = os.path.dirname(os.path.abspath(__file__))
# Add the project base directory to sys.path to make 'triposg' module discoverable
if triposg_base_dir not in sys.path:
    sys.path.insert(0, triposg_base_dir)


@app.post("/generate-3d-model")
async def generate_3d_model(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PNG or JPG image.",
        )

    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    ) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        image_path = temp_file.name

    try:
        # Generate a unique filename for the output GLB
        output_glb_name = f"generated_model_{uuid.uuid4().hex}.glb"
        output_glb_path = os.path.join(tempfile.gettempdir(), output_glb_name)

        # Construct the command to run the TripoSG inference script
        command = [
            "python",
            os.path.join(triposg_base_dir, "scripts", "inference_triposg.py"),
            "--image-input",
            image_path,
            "--output-path",
            output_glb_path,
        ]

        # Execute the inference script, setting cwd to the TripoSG base directory
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=triposg_base_dir
        )
        print("TripoSG stdout:", result.stdout)
        print("TripoSG stderr:", result.stderr)

        if not os.path.exists(output_glb_path):
            raise HTTPException(
                status_code=500,
                detail=f"GLB model not found at {output_glb_path}. Details: {result.stderr}",
            )

        # Return the generated GLB file
        return FileResponse(
            path=output_glb_path,
            filename=output_glb_name,
            media_type="model/gltf-binary",
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"TripoSG inference failed. Error: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        # Clean up the temporary input file
        if os.path.exists(image_path):
            os.unlink(image_path)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
