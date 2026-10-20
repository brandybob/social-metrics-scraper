# Use the official Apify Python Playwright image (pre-installs Chromium, Firefox, & dependencies)
FROM apify/actor-python-playwright:3.11

# Copy project files into the container
COPY . ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the main script
CMD ["python", "main.py"]