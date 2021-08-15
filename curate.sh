echo "URL of Reddit post: $1"

echo "Scraping Reddit page..."

mkdir data
python3 bin/get_post.py $1 > data/post.json

echo "Constructing comment tree..."
