# 1. Usa a imagem base oficial mais estável (Ubuntu 22.04)
FROM ardupilot/ardupilot-dev-base:latest

# 2. Instala as ferramentas essenciais de rede para o Mininet-WiFi
RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    net-tools \
    tcpdump \
    iperf3 \
    && rm -rf /var/lib/apt/lists/*

# 3. Instala o MAVProxy (Console de controle) e a biblioteca MAVLink
RUN pip3 install mavproxy pymavlink

# 3. Clona o código-fonte do ArduPilot (trazendo o código do drone para o container)
WORKDIR /ardupilot
RUN git clone https://github.com/ArduPilot/ardupilot.git . \
    && git submodule update --init --recursive

# 4. Compila o SITL (Software In The Loop) para Quadricópteros
RUN ./waf configure --board sitl
RUN ./waf copter

# 5. Adiciona os scripts (como sim_vehicle.py) no PATH do container
ENV PATH="/root/.local/bin:${PATH}"
ENV PATH="/ardupilot/Tools/autotest:${PATH}"
ENV PATH="/ardupilot/build/sitl/bin:${PATH}"

# 6. Mantém o container aberto e aguardando comandos do Containernet
CMD ["/bin/bash"]FROM ardupilot/ardupilot-dev-base:latest

RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    net-tools \
    tcpdump \
    iperf3 \
    && rm -rf /var/lib/apt/lists/*

    


