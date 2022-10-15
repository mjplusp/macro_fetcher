# macro_fetcher
Macro data crawler for investing.com

## mount network directory
sudo mkdir /mnt/z
sudo mount -t drvfs Z: /mnt/z

## docker commands
docker build -t macrofetcher:latest .
docker run -v "/mnt/d/alpha-distillery/macro_fetcher/app/_database:/usr/src/app/_database" --name macrofetcher macrofetcher
docker run -v "/mnt/z/macrodata:/usr/src/app/_database" --name macrofetcher macrofetcher