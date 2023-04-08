cd ../db
mkdir -p backups
cp -v "gamedata.db" backups/"gamedata"$(date +_%m-%d-%y).db
done