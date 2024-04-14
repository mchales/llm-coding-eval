# Use an official Python runtime as a parent image, anything above 3.7 should work
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run setup.py to install the package
RUN python setup.py install

ENV NAME World

CMD ["/bin/bash"]
