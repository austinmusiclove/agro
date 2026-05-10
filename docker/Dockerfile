# Use the official AWS Lambda Python image for 2026
FROM public.ecr.aws/lambda/python:3.12

# 1. Install specific AL2023 dependencies
# We use dnf and lowercase package names which are required now.
RUN dnf install -y \
    atk \
    at-spi2-atk \
    at-spi2-core \
    alsa-lib \
    cups-libs \
    gtk3 \
    libdrm \
    mesa-libgbm \
    libxkbcommon \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    nss \
    nspr \
    xorg-x11-server-Xvfb \
    xorg-x11-xauth \
    dbus-glib \
    google-noto-sans-fonts && \
    dnf clean all

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# 3. Tell Playwright where to put the browser
# This ensures it stays inside the Lambda image layers
ENV PLAYWRIGHT_BROWSERS_PATH=/var/task/pw-browsers
RUN playwright install chromium

# Copy your code
COPY lib ${LAMBDA_TASK_ROOT}/lib
COPY config ${LAMBDA_TASK_ROOT}/config

# Set the default command to your handler; this is overwritten for some functions
CMD [ "lib.lambdas.scrape_event_list.scrape_event_list" ]
