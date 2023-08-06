# Dockerfile for zhmc-os-forwarder project
#
# This image runs the zhmc_os_forwarder command.
# The standard metric definition file is provided in its default location, so
# the -m option does not need to be specified.
#
# The HMC credentials file still needs to be made available to the container
# using some mount option and specified with -c.
#
# Example docker command to run the forwarder using a locally built version of this image:
#
#   docker run -it --rm -v $(pwd)/myconfig:/root/myconfig -p 514:514 zhmcosforwarder -c /root/myconfig/config.yaml -v

FROM python:3.9-slim

# Install this package
ENV TMP_DIR=/tmp/zhmc-os-forwarder
WORKDIR $TMP_DIR
COPY . $TMP_DIR
RUN pip install . && rm -rf $TMP_DIR

# Set the current directory when running this image
WORKDIR /root

EXPOSE 9291
ENTRYPOINT ["zhmc_os_forwarder"]
CMD ["--help"]
