FROM nvidia/cuda:12.3.1-devel-ubuntu20.04

VOLUME ["/app"]
WORKDIR /app

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    build-essential \
    libxml2-dev \
    curl \
    wget \
    git \
    ffmpeg \
    ack \
    vim \
    apt-utils

RUN DEBIAN_FRONTEND=noninteractive apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install -y python3.7 \
    python3.7-distutils && \
    ln -sf /usr/bin/python3.7 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.7 /usr/bin/python && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py

RUN pip install torch torchvision torchaudio \
    wandb matplotlib einops p_tqdm youtube-dl gdown accelerate \
    git+https://github.com/rodrigo-castellon/jukemirlib.git
RUN pip install git+https://github.com/facebookresearch/pytorch3d.git
RUN gdown https://drive.google.com/uc?id=1BAR712cVEqB8GR37fcEihRV_xOC-fZrZ


CMD ["python", "test.py"]
