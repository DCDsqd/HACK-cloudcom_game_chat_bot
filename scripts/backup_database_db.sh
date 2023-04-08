cd ../db
mkdir -p backups
cp -v "database.db" backups/"database"$(date +_%m-%d-%y).db
done