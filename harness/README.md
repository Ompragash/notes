# Running Harness Delegate and Drone Runner Containers with Systemd

## Starting the Containers

- Start the Drone Runner Container:

```bash
sudo docker run -d --name=drone-runner-aws -v ./runner:/runner -p 3000:3000 drone/drone-runner-aws:latest  delegate --pool /runner/pool.yml
```
> _**Note:**_ Start runner in detach mode `-d` to run it in background and give a name `--name=drone-runner-aws`

- Start the Harness Delegate:

```bash
docker run  --cpus=1 --memory=2g \
  -d --name=harness-delegate \
  -e DELEGATE_NAME=docker-delegate \
  -e NEXT_GEN="true" \
  -e DELEGATE_TYPE="DOCKER" \
  -e ACCOUNT_ID=$ACCOUNT_ID \
  -e DELEGATE_TOKEN=$DELEGATE_TOKEN \
  -e DELEGATE_TAGS="" \
  -e LOG_STREAMING_SERVICE_URL=https://app.harness.io/gratis/log-service/ \
  -e MANAGER_HOST_AND_PORT=https://app.harness.io/gratis ghcr.io/delegate-image
```

> _**Note:**_ Start Harness Delegate in detach mode `-d` to run it in background and give a name `--name=harness-delegate`

## Setting Up Systemd Services

- Clone the Repository and Change Directory

```bash
git clone https://github.com/Ompragash/notes && cd notes
```

- Copy the Service Files to the Systemd Path

```bash
sudo cp ./harness/harness-delegate.service /etc/systemd/system/
sudo cp ./harness/drone-runner-aws.service /etc/systemd/system/
```

> _**Note:**_ The service file contains the command ExecStart=/usr/bin/docker start -a harness-delegate, so it’s important to start the delegate with the name harness-delegate. The same applies to the drone runner drone-runner-aws.

- Enable and Start the Services

```bash
sudo systemctl enable harness-delegate.service drone-runner-aws.service
sudo systemctl start harness-delegate.service drone-runner-aws.service
```

- Check the Service Status

```bash
sudo systemctl status harness-delegate.service drone-runner-aws.service
```
Example Output:
~~~
● harness-delegate.service - Harness Delegate Docker Container
     Loaded: loaded (/etc/systemd/system/harness-delegate.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2024-07-03 17:53:18 UTC; 12min ago
   Main PID: 1120 (docker)
      Tasks: 8 (limit: 9497)
     Memory: 18.0M
        CPU: 49ms
     CGroup: /system.slice/harness-delegate.service
             └─1120 /usr/bin/docker start -a harness-delegate

Jul 03 17:53:18 ip-172-31-0-244 systemd[1]: Started Harness Delegate Docker Container.

● drone-runner-aws.service - Drone Runner AWS Docker Container
     Loaded: loaded (/etc/systemd/system/drone-runner-aws.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2024-07-03 17:53:18 UTC; 12min ago
   Main PID: 1119 (docker)
      Tasks: 8 (limit: 9497)
     Memory: 22.3M
        CPU: 52ms
     CGroup: /system.slice/drone-runner-aws.service
             └─1119 /usr/bin/docker start -a drone-runner-aws

Jul 03 17:53:18 ip-172-31-0-244 systemd[1]: Started Drone Runner AWS Docker Container.
~~~
