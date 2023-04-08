cd ../db
mkdir -p backups
for f in *.db
do 
   cp -v "$f" backups/"${f%.db}"$(date +_%m-%d-%y).db
done