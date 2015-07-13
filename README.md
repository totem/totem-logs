# totem-logs
Microservice that provides API for accessing application logs deployed on totem.

## Status
In Development

## Running

### Docker
```
sudo docker run -v /dev/log:/dev/log --rm -p 9500:9500 -it --name totem-logs  totem/totem-logs
```
