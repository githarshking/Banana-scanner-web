# Use Python 3.9
FROM python:3.9

# Set working directory
WORKDIR /code

# Copy the requirements file
COPY ./api_requirements.txt /code/requirements.txt

# Install dependencies
# We ensure standard torch is installed (CPU version) to keep image size reasonable
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application files
COPY ./app.py /code/app.py
COPY ./predict_logic.py /code/predict_logic.py
COPY ./best_banana_ripeness_resnet.pth /code/best_banana_ripeness_resnet.pth

# Create a non-root user (Security requirement for HF Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose the port Hugging Face expects (7860)
EXPOSE 7860

# Start the server on port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]