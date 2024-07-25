# Scraper & API for Storm Tracker App

This repo has two parts:

1. Scrape data from various Weather Sources
2. Host API to support [stormtracker-app](<https://github.com/ddxv/stormtracker-app>)

## Scraper

Currently, scrapes data and directly plots the data, saving the output as PNG to a local `exported-images/` directory.

Run:
`python generate_storm_plots.py`

Pulling data from sources can be quite slow, a `-t` or `--test` flag will pickle data for subsequent runs.
`python generate_storm_plots.py -t`

## API Service

This API returns a list of storms `/storms` and then an image for each image type available:

`api/storms/{date}/{storm_id}/{image_type}`

image types: compare, myplot, tropycal

## Setup

- Current setup is based on Python3.11
- pip install dependencies, found in pyproject.toml: `pip install pandas requests litestar uvicorn gunicorn tropycal pygrib shapely cartopy`

Installing tropycal and pygrib required unique steps in my environment, so likely you will need to check their documentation for your own installation.

## Running Locally

- To run locally for testing use
  - `$ gunicorn -k uvicorn.workers.UvicornWorker app:app`

## Running in production

To setup the API for production requires 3 files outside of this project to be set. Two systemctl systemd unit files: service & socket. The third file is the nginx configuration to point HTTP traffic to the unix socket.

### Socket Unit File

location: `/etc/systemd/system/stormtracker-api.socket`

```Shell
[Unit]
Description=Gunicorn socket

[Socket]
ListenStream=/run/stormtracker-api.sock
User=www-data

[Install]
WantedBy=sockets.target
```

### Service Unit file

location: `/etc/systemd/system/stormtracker-api.service`

```Shell
[Unit]
Description=Gunicorn instance to serve StormTracker API
After=network.target

[Service]
Type=Notify
User=ubuntu
Group=ubuntu
RuntimeDirectory=gunicorn
WorkingDirectory=/home/ubuntu/stormtracker-api
Environment="PROD=True" /home/ubuntu/venvs/stormtracker-env/bin
ExecStart=/home/ubuntu/venv/stormtracker-env/bin/gunicorn -k uvicorn.workers.UvicornWorker --workers 1 --bind unix:stormtracker-api.sock -m 007 app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Nginx config file

This is wherever you have your nginx configuration set, possibly sites-available `/etc/nginx/sites-available/stormtracker-api` or `/etc/nginx/conf.d/stormtracker-api.conf`

`stormtracker-api`

```Nginx
server {
    listen 80;
    client_max_body_size 2M;

    location /api {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-NginX-Proxy true;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://unix:/run/stormtracker-api.sock;
    }
}
```

If you put your nginx configuration in a new file in sites-available, be sure to link to sites-enabled to start:

```Shell
sudo ln -s /etc/nginx/sites-available/stormtracker-api /etc/nginx/sites-enabled/stormtracker-api
sudo systemctl restart nginx.service 
```

## Start the service and socket

- `systemctl enable stormtracker-api.socket` to automatically start socket on server reboot
- `sudo systemctl start stormtracker-api.socket` star
- `sudo systemctl status stormtracker-api` to check status

## Check your API endpoints

try visiting example.com/api/storms/

## Troubleshooting

Checking your local API docs:

`http://127.0.0.1:8000/api/docs`

Restarting Unit service
- `sudo systemctl stop stormtracker-api`
- `sudo systemctl start stormtracker-api`

